"""dirdump — собирает дерево каталога в один файл для передачи нейросетям."""

from dirdump._version import __version__
from dirdump.collector import FileEntry, collect
from dirdump.renderers import render

__all__ = ["FileEntry", "collect", "render", "__version__"]
