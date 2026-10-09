"""Обход дерева каталогов и подготовка записей для рендеринга."""

from __future__ import annotations

import fnmatch
import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from dirdump.detectors import is_binary
from dirdump.gitignore import GitignoreStack


@dataclass(frozen=True)
class FileEntry:
    """Один файл, отобранный для дампа."""

    path: Path          # путь относительно корня
    size: int           # размер в байтах на диске
    content: str | None # None, если файл бинарный или не читается
    is_binary: bool
    truncated: bool


@dataclass
class CollectorOptions:
    """Настройки для функции `collect`."""

    root: Path
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    max_bytes: int = 200_000
    use_gitignore: bool = True
    check_binary: bool = True
    encoding: str = "utf-8"


def _matches_any(rel_posix: str, patterns: tuple[str, ...]) -> bool:
    """Проверяет, совпадает ли путь хотя бы с одним из glob-шаблонов."""
    return any(fnmatch.fnmatch(rel_posix, p) for p in patterns)


def collect(opts: CollectorOptions) -> Iterator[FileEntry]:
    """Обходит `opts.root` и возвращает `FileEntry` в отсортированном порядке.

    Учитывает `.gitignore`, фильтры include/exclude, определение бинарных
    файлов и лимит на размер файла. Никогда не загружает всё дерево в память.
    """
    root = opts.root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Не каталог: {root}")

    gitignore = GitignoreStack()

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)

        # Загружаем .gitignore текущего каталога.
        if opts.use_gitignore:
            gitignore.push(current)

        # Фильтруем подкаталоги на месте, чтобы os.walk их пропустил.
        kept_dirs: list[str] = []
        for d in sorted(dirnames):
            full = current / d
            rel = full.relative_to(root)
            if opts.use_gitignore and gitignore.is_ignored(full, root, is_dir=True):
                continue
            if opts.exclude and _matches_any(rel.as_posix() + "/", opts.exclude):
                continue
            kept_dirs.append(d)
        dirnames[:] = kept_dirs

        # Обрабатываем файлы текущего каталога.
        for name in sorted(filenames):
            full = current / name
            rel = full.relative_to(root)
            rel_posix = rel.as_posix()

            if opts.use_gitignore and gitignore.is_ignored(full, root, is_dir=False):
                continue
            if opts.exclude and _matches_any(rel_posix, opts.exclude):
                continue
            if opts.include and not _matches_any(rel_posix, opts.include):
                continue

            try:
                size = full.stat().st_size
            except OSError:
                continue

            binary = opts.check_binary and is_binary(full)
            content: str | None = None
            truncated = False

            if not binary:
                try:
                    raw = full.read_text(encoding=opts.encoding, errors="replace")
                except OSError:
                    binary = True
                else:
                    if len(raw) > opts.max_bytes:
                        raw = raw[: opts.max_bytes] + (
                            f"\n...<обрезано, всего {size} байт>\n"
                        )
                        truncated = True
                    content = raw

            yield FileEntry(
                path=rel,
                size=size,
                content=content,
                is_binary=binary,
                truncated=truncated,
            )

        # Снимаем правила .gitignore после обхода каталога.
        if opts.use_gitignore:
            gitignore.pop(current)
