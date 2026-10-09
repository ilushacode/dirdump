"""Тесты оценки токенов."""

from dirdump.tokens import estimate_tokens, format_token_count


def test_estimate_tokens_positive() -> None:
    """Оценка всегда ≥ 1."""
    assert estimate_tokens("привет мир") >= 1


def test_estimate_scales_with_length() -> None:
    """Оценка растёт с длиной текста."""
    short = estimate_tokens("привет")
    long = estimate_tokens("привет " * 1000)
    assert long > short


def test_format_small() -> None:
    """Малые значения без сокращений."""
    assert format_token_count(500) == "500 токенов"


def test_format_kilo() -> None:
    """Тысячи сокращаются как k."""
    assert format_token_count(12_300) == "12.3k токенов"


def test_format_mega() -> None:
    """Миллионы сокращаются как M."""
    assert format_token_count(2_500_000) == "2.50M токенов"
