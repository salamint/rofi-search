"""
File containing the Browser class definition,
as well as some default browser values.

The selection of browsers include a small variety of Firefox
and Chromium base browsers, but a lot are missing.
Note that also some browsers are using the gecko web engine,
and are not based on Firefox, but are still marked as based
off Firefox.
There might also be browsers flagged as private, that are
not actually private, or not flagged as private, that are
actually private.
Please report any mistake on GitHub.
If you suffer any inconvenience, you can always change the
configuration to accept exceptions.

Please feel free to request any browser that you would
like to see supported.
"""
import subprocess
from shutil import which
from typing import Optional

from search_engine import SearchEngine


class Browser:
    """
    Class describing a browser as an executable.
    Its name is referring to the executable's name,
    which are case-sensitive.
    A browser can also have a list of options that
    are required to properly start a search query.
    A browser also contains some rudimentary metadata,
    like if it is private (cares about privacy), or on
    which browser/eweb engine it is based on.

    There are 2 main browser families/web engines:
    - Firefox (Gecko web engine)
    - Chromium
    Anything that is a fork of one of these or uses
    one of them as a backend are considered based on it.
    e.g. LibreWolf is a fork of Firefox, therefore,
    LibreWolf is based on Firefox.
    """

    all: dict[str, 'Browser'] = {}

    def __new__(cls, name: str, *args, **kwargs):
        obj = super().__new__(cls)
        cls.all[name] = obj
        return obj

    def __init__(self, name: str, arguments: Optional[list[str]] = None, private: bool = False, base: Optional['Browser'] = None, search_engine: Optional['SearchEngine'] = None, private_arguments: Optional[list[str]] = None):
        self.name = name
        self.arguments = arguments if arguments is not None else []
        self.private = private
        self.base = base
        self.search_engine = search_engine
        self.private_arguments = private_arguments if private_arguments is not None else []

    def __str__(self) -> str:
        private_string = ", private" if self.is_private() else ""
        based_on_string = f", based on {self.get_base().get_name()}" if self.get_base() is not None else ""
        return f'<{self.__class__.__name__} "{self.get_name()}"{private_string}{based_on_string}>'

    def get_name(self) -> str:
        return self.name

    def get_arguments(self) -> list[str]:
        return self.arguments

    def get_base(self) -> Optional['Browser']:
        return self.base

    def get_search_engine(self) -> Optional['SearchEngine']:
        return self.search_engine

    def is_private(self) -> bool:
        return self.private

    def is_installed(self) -> bool:
        return which(self.get_name()) is not None

    def get_command(self, url: str, private: bool = False) -> list[str]:
        command = [self.get_name()]
        command.extend(self.get_arguments())
        if private:
            command.extend(self.private_arguments)
        command.append(url)
        return command

    def spawn(self, url: str, private: bool = False):
        return subprocess.run(self.get_command(url))


class BrowserException(Exception):
    pass


CHROMIUM = Browser("chromium", [])
FIREFOX = Browser("firefox", private_arguments=["--private-window"])

BRAVE = Browser("brave", [], private=True, base=CHROMIUM)
CHROME = Browser("chrome", [], base=CHROMIUM)
FLOORP = Browser("floorp", [], private=True, base=FIREFOX)
ICECAT = Browser("icecat", [], private=True, base=FIREFOX)
LIBREWOLF = Browser("librewolf", [], private=True, base=FIREFOX, private_arguments=["--private-window"])
OPERA = Browser("opera", [], base=CHROMIUM)
PALEMOON = Browser("palemoon", [], private=True, base=FIREFOX)
QUTEBROWSER = Browser("qutebrowser", [], base=CHROMIUM, private_arguments=["--target", "private-window"])
TOR = Browser("tor", [], base=FIREFOX)
UNGOOGLED_CHROMIUM = Browser("ungoogled_chromium", [], private=True, base=CHROMIUM)
VIVALDI = Browser("vivaldi", [], base=CHROMIUM)
WATERFOX = Browser("waterfox", [], private=True, base=FIREFOX)
ZEN = Browser("zen-browser", [], private=True, base=FIREFOX)