import builtins
import site
import sys
from pathlib import Path

from .version import VERSION

# language=python
install_code = """
# add devtools `debug` function to builtins
# we don't want to import devtools until it's required since it breaks pytest, hence this proxy
class DebugProxy:
    def __init__(self):
        self._debug = None

    def _import_debug(self):
        if self._debug is None:
            from devtools import debug
            self._debug = debug

    def __call__(self, *args, **kwargs):
        self._import_debug()
        kwargs['frame_depth_'] = 3
        return self._debug(*args, **kwargs)

    def format(self, *args, **kwargs):
        self._import_debug()
        kwargs['frame_depth_'] = 3
        return self._debug.format(*args, **kwargs)

    def __getattr__(self, item):
        self._import_debug()
        return getattr(self._debug, item)

import builtins
setattr(builtins, 'debug', DebugProxy())
"""


def print_code() -> int:
    print(install_code)
    return 0


def install() -> int:
    # Really do the installation instead of telling what to do
    paths = [Path(p) for p in site.getsitepackages()]
    path = next(p for p in paths if p.exists())
    sc = path / 'sitecustomize.py'

    if hasattr(builtins, 'debug'):
        print(f'Looks like devtools is already installed, probably in `{sc}`.')
        return 0

    with sc.open('a') as fh:
        fh.write(install_code)

    return 0


if __name__ == '__main__':
    if 'install' in sys.argv:
        sys.exit(install())
    elif 'print-code' in sys.argv:
        sys.exit(print_code())
    else:
        print(f'python-devtools v{VERSION}, CLI usage: `python -m devtools install|print-code`')
        sys.exit(1)
