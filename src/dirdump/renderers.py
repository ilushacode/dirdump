"""Рендеринг потока `FileEntry` в текст, JSON или Markdown."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import TextIO

from dirdump._version import __version__
from dirdump.collector import FileEntry

# Все поддерживаемые форматы вывода.
_FORMATS = ("text", "json", "markdown")


def render(
    entries: Iterable[FileEntry],
    *,
    root_display: str,
    fmt: str,
    out: TextIO,
) -> None:
    """Рендерит `entries` в `out` в выбранном формате."""
    if fmt not in _FORMATS:
        raise ValueError(f"Неизвестный формат: {fmt!r}. Доступны: {_FORMATS}.")

    if fmt == "text":
        _render_text(entries, root_display=root_display, out=out)
    elif fmt == "json":
        _render_json(entries, root_display=root_display, out=out)
    else:
        _render_markdown(entries, root_display=root_display, out=out)


def _header(root_display: str) -> str:
    """Общий заголовок дампа для текстового формата."""
    return (
        f"# Дамп каталога: {root_display}\n"
        f"# Сгенерировано dirdump {__version__}\n"
    )


def _render_text(
    entries: Iterable[FileEntry], *, root_display: str, out: TextIO
) -> None:
    """Текстовый формат с маркерами `=== ФАЙЛ: ... ===`."""
    out.write(_header(root_display))
    for entry in entries:
        out.write(f"\n=== ФАЙЛ: {entry.path.as_posix()} ===\n")
        if entry.is_binary:
            out.write(f"<бинарный файл, {entry.size} байт>\n")
        else:
            out.write(entry.content or "")


def _render_json(
    entries: Iterable[FileEntry], *, root_display: str, out: TextIO
) -> None:
    """Структурированный JSON для программной обработки."""
    payload = {
        "root": root_display,
        "generator": f"dirdump {__version__}",
        "files": [
            {
                "path": e.path.as_posix(),
                "size": e.size,
                "is_binary": e.is_binary,
                "truncated": e.truncated,
                "content": e.content,
            }
            for e in entries
        ],
    }
    json.dump(payload, out, ensure_ascii=False, indent=2)
    out.write("\n")


def _markdown_lang(path: str) -> str:
    """Определяет язык для блока ``` по расширению файла."""
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "rb": "ruby",
        "rs": "rust",
        "go": "go",
        "sh": "bash",
        "bash": "bash",
        "yml": "yaml",
        "yaml": "yaml",
        "toml": "toml",
        "json": "json",
        "md": "markdown",
        "html": "html",
        "css": "css",
    }.get(ext, "")


def _render_markdown(
    entries: Iterable[FileEntry], *, root_display: str, out: TextIO
) -> None:
    """Markdown с заголовками и подсветкой синтаксиса."""
    out.write(f"# Дамп каталога\n\n**Корень:** `{root_display}`\n\n")
    out.write(f"_Сгенерировано dirdump {__version__}._\n")
    for entry in entries:
        rel = entry.path.as_posix()
        out.write(f"\n## `{rel}`\n\n")
        if entry.is_binary:
            out.write(f"*Бинарный файл, {entry.size} байт.*\n")
            continue
        lang = _markdown_lang(rel)
        out.write(f"```{lang}\n")
        out.write(entry.content or "")
        if not (entry.content or "").endswith("\n"):
            out.write("\n")
        out.write("```\n")
