"""Тесты определения бинарных файлов."""

from pathlib import Path

from dirdump.detectors import is_binary


def test_text_file_is_not_binary(tmp_path: Path) -> None:
    """Текстовый файл не должен считаться бинарным."""
    p = tmp_path / "a.txt"
    p.write_text("привет мир\n")
    assert is_binary(p) is False


def test_binary_file_is_detected(tmp_path: Path) -> None:
    """Файл с нулевыми байтами определяется как бинарный."""
    p = tmp_path / "a.bin"
    p.write_bytes(b"\x00\x01\x02\x03")
    assert is_binary(p) is True


def test_empty_file_is_not_binary(tmp_path: Path) -> None:
    """Пустой файл - не бинарный."""
    p = tmp_path / "empty"
    p.write_bytes(b"")
    assert is_binary(p) is False


def test_missing_file_is_treated_as_binary(tmp_path: Path) -> None:
    """Отсутствующий файл считается бинарным (безопасное поведение)."""
    assert is_binary(tmp_path / "nope") is True
