"""Командный интерфейс dirdump."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import TextIO

from dirdump._version import __version__
from dirdump.collector import CollectorOptions, FileEntry, collect
from dirdump.renderers import render
from dirdump.tokens import estimate_tokens, format_token_count, has_tiktoken


def build_parser() -> argparse.ArgumentParser:
    """Собирает парсер аргументов командной строки."""
    p = argparse.ArgumentParser(
        prog="dirdump",
        description=(
            "Собирает дерево каталога в один файл — удобно для передачи "
            "нейросети в качестве контекста."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("directory", type=Path, help="Корневой каталог для дампа.")
    p.add_argument(
        "-o",
        "--output",
        default="-",
        help="Выходной файл. Используйте '-' для вывода в stdout.",
    )
    p.add_argument(
        "-f",
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Формат вывода.",
    )
    p.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="ШАБЛОН",
        help="Включать только файлы, совпадающие с ШАБЛОНом. Можно повторять.",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="ШАБЛОН",
        help="Исключать файлы и каталоги, совпадающие с ШАБЛОНом. Можно повторять.",
    )
    p.add_argument(
        "--max-bytes",
        type=int,
        default=200_000,
        help="Обрезать содержимое файла после стольких байт.",
    )
    p.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Не учитывать файлы .gitignore.",
    )
    p.add_argument(
        "--no-binary-check",
        action="store_true",
        help="Считать все файлы текстовыми (может дать мусор для бинарников).",
    )
    p.add_argument(
        "--encoding",
        default="utf-8",
        help="Кодировка для чтения текстовых файлов.",
    )
    p.add_argument(
        "--tokens",
        action="store_true",
        help="Вывести оценку количества токенов в stderr после записи.",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Не выводить итоговую сводку в stderr.",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"dirdump {__version__}",
    )
    return p


def _open_output(path: str) -> tuple[TextIO, bool]:
    """Открывает выходной поток. `-` означает stdout.

    Файлы записываются в UTF-8 с BOM (`utf-8-sig`) и с переносами строк
    `\\n` — так дамп корректно открывается в «Блокноте» на Windows и при
    этом остаётся одинаковым на всех ОС. Stdout BOM не получает.

    Возвращает пару `(поток, нужно_ли_закрывать)`.
    """
    if path == "-":
        return sys.stdout, False
    return open(path, "w", encoding="utf-8-sig", newline="\n"), True


def main(argv: Sequence[str] | None = None) -> int:
    """Точка входа CLI. Возвращает код выхода."""
    args = build_parser().parse_args(argv)

    root = args.directory
    if not root.exists():
        print(f"ошибка: путь не существует: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"ошибка: это не каталог: {root}", file=sys.stderr)
        return 2

    opts = CollectorOptions(
        root=root,
        include=tuple(args.include),
        exclude=tuple(args.exclude),
        max_bytes=args.max_bytes,
        use_gitignore=not args.no_gitignore,
        check_binary=not args.no_binary_check,
        encoding=args.encoding,
    )

    stream, should_close = _open_output(args.output)
    try:
        # Если запрошена оценка токенов, материализуем список, чтобы можно
        # было переиспользовать его для подсчёта. Иначе стримим напрямую.
        # Аннотация Iterable[FileEntry] объединяет оба случая для mypy.
        entries: Iterable[FileEntry]
        if args.tokens:
            entries = list(collect(opts))
        else:
            entries = collect(opts)
        render(entries, root_display=str(root.resolve()), fmt=args.format, out=stream)
    finally:
        if should_close:
            stream.close()
        else:
            stream.flush()

    if args.tokens:
        try:
            text = (
                Path(args.output).read_text(encoding="utf-8-sig")
                if args.output != "-"
                else ""
            )
        except OSError:
            text = ""
        if text:
            n = estimate_tokens(text)
            exact = "точно" if has_tiktoken() else "приблизительно"
            print(
                f"[dirdump] {format_token_count(n)} ({exact})",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
