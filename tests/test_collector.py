"""Тесты обхода дерева каталогов."""

from pathlib import Path

import pytest

from dirdump.collector import CollectorOptions, collect


def _paths(entries) -> list[str]:
    """Утилита: вытащить пути из записей."""
    return [e.path.as_posix() for e in entries]


def test_collects_text_files(sample_tree: Path) -> None:
    """Текстовые файлы попадают в дамп."""
    entries = list(collect(CollectorOptions(root=sample_tree)))
    paths = _paths(entries)
    assert "README.md" in paths
    assert "src/main.py" in paths
    assert "src/util.py" in paths


def test_gitignore_excludes_node_modules(sample_tree: Path) -> None:
    """node_modules и *.log исключаются благодаря .gitignore."""
    entries = list(collect(CollectorOptions(root=sample_tree)))
    paths = _paths(entries)
    assert not any("node_modules" in p for p in paths)
    assert "debug.log" not in paths


def test_gitignore_can_be_disabled(sample_tree: Path) -> None:
    """При use_gitignore=False .gitignore не учитывается."""
    entries = list(collect(CollectorOptions(root=sample_tree, use_gitignore=False)))
    paths = _paths(entries)
    assert any("node_modules" in p for p in paths)


def test_include_filter(sample_tree: Path) -> None:
    """--include оставляет только подходящие файлы."""
    entries = list(collect(CollectorOptions(root=sample_tree, include=("*.py",))))
    paths = _paths(entries)
    assert paths == ["src/main.py", "src/util.py"]


def test_exclude_filter(sample_tree: Path) -> None:
    """--exclude убирает подходящие файлы."""
    entries = list(collect(CollectorOptions(root=sample_tree, exclude=("*.md",))))
    paths = _paths(entries)
    assert "README.md" not in paths


def test_binary_detection(sample_tree: Path) -> None:
    """Бинарные файлы помечаются, содержимое не читается."""
    entries = {e.path.as_posix(): e for e in collect(CollectorOptions(root=sample_tree))}
    assert entries["logo.png"].is_binary is True
    assert entries["logo.png"].content is None
    assert entries["README.md"].is_binary is False


def test_truncation(tmp_path: Path) -> None:
    """Большие файлы обрезаются до --max-bytes."""
    big = tmp_path / "big.txt"
    big.write_text("a" * 10_000)
    entries = list(collect(CollectorOptions(root=tmp_path, max_bytes=100)))
    e = entries[0]
    assert e.truncated is True
    assert len(e.content or "") < 10_000
    assert "обрезано" in (e.content or "")


def test_invalid_directory(tmp_path: Path) -> None:
    """Несуществующий каталог - исключение NotADirectoryError."""
    with pytest.raises(NotADirectoryError):
        list(collect(CollectorOptions(root=tmp_path / "nope")))
