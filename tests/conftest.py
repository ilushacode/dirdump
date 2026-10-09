"""Общие фикстуры pytest."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_tree(tmp_path: Path) -> Path:
    """Небольшое реалистичное дерево каталогов для тестов."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('привет')\n")
    (tmp_path / "src" / "util.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp_path / "README.md").write_text("# Пример\n")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x00binary")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "junk.js").write_text("мусор\n")
    (tmp_path / ".gitignore").write_text("node_modules/\n*.log\n")
    (tmp_path / "debug.log").write_text("шум\n")
    return tmp_path
