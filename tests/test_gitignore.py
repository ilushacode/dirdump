"""Тесты работы со стеком .gitignore."""

from pathlib import Path

from dirdump.gitignore import GitignoreStack


def test_simple_pattern(tmp_path: Path) -> None:
    """Простой шаблон `*.log` игнорирует .log-файлы."""
    (tmp_path / ".gitignore").write_text("*.log\n")
    stack = GitignoreStack()
    stack.push(tmp_path)
    assert stack.is_ignored(tmp_path / "a.log", tmp_path, is_dir=False) is True
    assert stack.is_ignored(tmp_path / "a.txt", tmp_path, is_dir=False) is False


def test_directory_pattern(tmp_path: Path) -> None:
    """Шаблон `build/` игнорирует одноимённый каталог."""
    (tmp_path / ".gitignore").write_text("build/\n")
    stack = GitignoreStack()
    stack.push(tmp_path)
    assert stack.is_ignored(tmp_path / "build", tmp_path, is_dir=True) is True


def test_nested_gitignore(tmp_path: Path) -> None:
    """Вложенный .gitignore действует только пока мы внутри каталога."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / ".gitignore").write_text("secret.txt\n")
    stack = GitignoreStack()
    stack.push(tmp_path)
    stack.push(sub)
    assert stack.is_ignored(sub / "secret.txt", tmp_path, is_dir=False) is True
    stack.pop(sub)
    assert stack.is_ignored(sub / "secret.txt", tmp_path, is_dir=False) is False
