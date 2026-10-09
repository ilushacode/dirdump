"""Тесты рендеринга в текст, JSON и Markdown."""

import io
import json
from pathlib import Path

import pytest

from dirdump.collector import FileEntry
from dirdump.renderers import render


def _entry(name: str, content: str | None, *, binary: bool = False) -> FileEntry:
    """Утилита: сконструировать FileEntry для тестов."""
    return FileEntry(
        path=Path(name),
        size=len(content or ""),
        content=content,
        is_binary=binary,
        truncated=False,
    )


def test_text_render() -> None:
    """Текстовый рендер содержит маркер файла и содержимое."""
    buf = io.StringIO()
    render(
        [_entry("a.py", "print(1)\n")],
        root_display="/root",
        fmt="text",
        out=buf,
    )
    out = buf.getvalue()
    assert "=== ФАЙЛ: a.py ===" in out
    assert "print(1)" in out


def test_json_render() -> None:
    """JSON-рендер возвращает валидный JSON с нужной структурой."""
    buf = io.StringIO()
    render(
        [_entry("a.py", "print(1)\n")],
        root_display="/root",
        fmt="json",
        out=buf,
    )
    data = json.loads(buf.getvalue())
    assert data["root"] == "/root"
    assert data["files"][0]["path"] == "a.py"


def test_markdown_render() -> None:
    """Markdown-рендер содержит заголовок и блок кода с языком."""
    buf = io.StringIO()
    render(
        [_entry("a.py", "print(1)\n")],
        root_display="/root",
        fmt="markdown",
        out=buf,
    )
    out = buf.getvalue()
    assert "## `a.py`" in out
    assert "```python" in out


def test_binary_marker_in_text() -> None:
    """Бинарный файл помечается в текстовом выводе."""
    buf = io.StringIO()
    render(
        [_entry("x.bin", None, binary=True)],
        root_display="/root",
        fmt="text",
        out=buf,
    )
    assert "бинарный файл" in buf.getvalue()


def test_unknown_format_raises() -> None:
    """Неизвестный формат вызывает ValueError."""
    with pytest.raises(ValueError):
        render([], root_display="/", fmt="xml", out=io.StringIO())
