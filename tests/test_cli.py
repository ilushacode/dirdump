"""Тесты командного интерфейса."""

from pathlib import Path

from dirdump.cli import main


def test_cli_writes_output(sample_tree: Path, tmp_path: Path) -> None:
    """CLI пишет дамп в указанный файл."""
    out = tmp_path / "dump.txt"
    rc = main([str(sample_tree), "-o", str(out), "-q"])
    assert rc == 0
    # Читаем явно в utf-8-sig: так корректно читается UTF-8 как с BOM,
    # так и без — и не зависим от кодировки по умолчанию на Windows.
    text = out.read_text(encoding="utf-8-sig")
    assert "=== ФАЙЛ: README.md ===" in text


def test_cli_missing_path(tmp_path: Path, capsys) -> None:
    """Несуществующий путь — код 2 и понятное сообщение."""
    rc = main([str(tmp_path / "nope")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "не существует" in err


def test_cli_not_a_directory(tmp_path: Path, capsys) -> None:
    """Путь к файлу вместо каталога — код 2."""
    f = tmp_path / "file.txt"
    f.write_text("x")
    rc = main([str(f)])
    assert rc == 2
    assert "не каталог" in capsys.readouterr().err


def test_cli_format_json(sample_tree: Path, tmp_path: Path) -> None:
    """Формат json даёт файл, начинающийся с {."""
    out = tmp_path / "dump.json"
    rc = main([str(sample_tree), "-o", str(out), "-f", "json", "-q"])
    assert rc == 0
    text = out.read_text(encoding="utf-8-sig")
    assert text.lstrip().startswith("{")
