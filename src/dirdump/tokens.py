"""Оценка количества токенов для бюджета контекста LLM."""

from __future__ import annotations

# Приблизительное среднее: один токен ≈ 4 символа английского текста или кода.
_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Оценивает количество токенов LLM в `text`.

    Если доступен `tiktoken` от OpenAI — используется он и даёт почти
    точную оценку. Иначе работает консервативная эвристика по символам.
    """
    try:
        import tiktoken
    except ImportError:
        return max(1, len(text) // _CHARS_PER_TOKEN)

    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def has_tiktoken() -> bool:
    """Доступен ли точный подсчёт токенов через tiktoken."""
    try:
        import tiktoken  # noqa: F401
    except ImportError:
        return False
    return True


def format_token_count(n: int) -> str:
    """Человекочитаемое представление, например `12.3k токенов`."""
    if n < 1_000:
        return f"{n} токенов"
    if n < 1_000_000:
        return f"{n / 1_000:.1f}k токенов"
    return f"{n / 1_000_000:.2f}M токенов"
