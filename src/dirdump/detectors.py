"""Эвристики для определения бинарных файлов и их кодировки."""

from __future__ import annotations

from pathlib import Path

# Сколько байт считываем с начала файла для анализа.
_SNIFF_SIZE = 8192


def is_binary(path: Path, sniff_size: int = _SNIFF_SIZE) -> bool:
    """Возвращает True, если файл выглядит бинарным.

    Использует классическую эвристику по нулевому байту: текстовые файлы
    практически никогда не содержат NUL-байт в первых килобайтах, а
    бинарные - почти всегда содержат.

    Если файл не удаётся прочитать, возвращаем True - безопаснее пропустить
    файл, чем встроить в дамп мусор.
    """
    try:
        with path.open("rb") as fh:
            chunk = fh.read(sniff_size)
    except OSError:
        return True
    if not chunk:
        return False
    return b"\x00" in chunk
