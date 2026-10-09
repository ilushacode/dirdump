"""Работа с `.gitignore` на основе библиотеки `pathspec`."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pathspec
from pathspec.patterns.gitignore.basic import GitIgnoreBasicPattern


@dataclass
class GitignoreStack:
    """Стек правил `.gitignore`, по одному на каждый уровень каталога.

    Каждый элемент — пара `(относительный_каталог_от_корня, PathSpec)`.
    При проверке пути учитываются спецификации всех его родительских
    каталогов.
    """

    _rules: list[tuple[Path, pathspec.PathSpec[GitIgnoreBasicPattern]]] = field(
        default_factory=list
    )

    def push(self, directory: Path) -> None:
        """Загружает `.gitignore` внутри `directory`, если он существует."""
        gi = directory / ".gitignore"
        if not gi.is_file():
            return
        try:
            text = gi.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        # Фабрика "gitignore" возвращает PathSpec[GitIgnoreBasicPattern].
        spec: pathspec.PathSpec[GitIgnoreBasicPattern] = pathspec.PathSpec.from_lines(
            "gitignore", text.splitlines()
        )
        self._rules.append((directory, spec))

    def pop(self, directory: Path) -> None:
        """Удаляет правила, загруженные для `directory`, если они есть."""
        if self._rules and self._rules[-1][0] == directory:
            self._rules.pop()

    def is_ignored(self, path: Path, root: Path, *, is_dir: bool) -> bool:
        """Возвращает True, если `path` попадает под любое активное правило.

        Пути сопоставляются относительно каталога каждого правила — так же,
        как git вычисляет вложенные `.gitignore`.
        """
        for base, spec in self._rules:
            try:
                rel = path.relative_to(base)
            except ValueError:
                continue
            rel_posix = rel.as_posix()
            if is_dir:
                rel_posix += "/"
            if spec.match_file(rel_posix):
                return True
        return False
