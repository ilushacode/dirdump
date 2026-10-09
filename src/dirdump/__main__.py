"""Позволяет запускать `python -m dirdump` как обычный `dirdump`."""

from dirdump.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
