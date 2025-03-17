import os
from argparse import Namespace
from pathlib import Path
from typing import Optional

from entries.browser import Browser, FIREFOX, BrowserException
from entries.search_engine import SearchEngine, DUCKDUCKGO, SearchEngineException

DEFAULT_ALIASES_COLOR = "#444444"
DEFAULT_LANGUAGE = 'en'
DEFAULT_SEARCH_ENGINE = DUCKDUCKGO


def get_system_locale() -> str:
    """
    Extracts the first 2 characters from the system locale.
    If you use the C locale, or you haven't set your locale,
    this will fallback to the default locale (see below).
    :return: A 2 character string representing the locale.
    """
    lang = os.getenv("LANG")
    if lang is None:
        return DEFAULT_LANGUAGE
    locale = lang[:2]
    if locale == "C.":
        return DEFAULT_LANGUAGE
    return locale


def get_user_browser() -> Optional['Browser']:
    return Browser.all.get(os.getenv("BROWSER"))


class Configuration:

    def __init__(self, debug: bool = False):
        self.files: list['Path'] = []
        self.debug = debug
        self.main = MainConfiguration()
        self.browsers = BrowserConfiguration()
        self.search_engines = SearchEngineConfiguration(self.browsers)
        self.customization = CustomizationConfig()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(lang="{self.main.get_language()}", browser="{self.browsers.get_browser().get_name()}", search_engine="{self.search_engines.get_search_engine().get_name()}")'

    def has_loaded(self, file: Path) -> bool:
        return file in self.files

    def load(self, file: 'Path'):
        if file not in self.files:
            self.files.append(file)


class MainConfiguration:

    def __init__(self):
        self.private_search: bool = False
        self.language: Optional[str] = None
        self.sources: list[Path] = []

    def get_language(self) -> str:
        """
        Gets the language to use for the search engine.
        This will use the preferred language if it was set,
        if it isn't, t will fallback on the system language.
        If it hasn't been set either, it will fallback on
        the default locale.
        :return: A 2 character string representing the language/locale (e.g. 'en' for english).
        """
        if self.language is None:
            return get_system_locale()
        return self.language

    def get_sources(self) -> list[Path]:
        return self.sources

    def is_private_search_enabled(self) -> bool:
        return self.private_search


class BrowserConfiguration:

    def __init__(self):
        self.explicit: Optional['Browser'] = None
        self.preferred: list['Browser'] = []
        self.private_only = False
        self.hide: list['Browser'] = []
        self.show: list['Browser'] = []
        self.hide_based_on: list['Browser'] = []
        self.show_based_on: list['Browser'] = []

    def get_all(self) -> list['Browser']:
        browsers = []
        for browser in Browser.all.values():
            if self.is_valid(browser):
                browsers.append(browser)
        return browsers

    def get_explicit(self) -> Optional['Browser']:
        if self.explicit is not None and self.explicit.is_installed():
            return self.explicit
        return None

    def get_preferred_browser(self) -> Optional['Browser']:
        for browser in self.preferred:
            if browser.is_installed():
                return browser
        return None

    def get_browser(self) -> 'Browser':
        explicit = self.get_explicit()
        if explicit is not None:
            return explicit
        preferred = self.get_preferred_browser()
        if preferred is not None:
            return preferred
        user_browser = get_user_browser()
        if user_browser is not None:
            return user_browser
        return FIREFOX

    def is_valid(self, browser: 'Browser') -> bool:
        if not browser.is_installed():
            return False

        if browser in self.show or browser in self.preferred:
            return True
        elif browser in self.hide:
            return False

        if self.private_only and not browser.is_private():
            return False

        base = browser.get_base()
        if base is None or base in self.show_based_on:
            return True
        elif base is not None and base in self.hide_based_on:
            return False
        return True

    def load_args(self, args: Namespace):
        preferred_browsers = args.preferred_browsers
        if preferred_browsers is not None:
            browser = Browser.all.get(preferred_browsers)
            if browser is None:
                raise BrowserException(f"No browser named '{preferred_browsers}' found.")
            if not browser.is_installed():
                raise BrowserException(f"Browser '{preferred_browsers}' is not installed on your machine or not in $PATH.")
            self.explicit = browser


class SearchEngineConfiguration:

    def __init__(self, browser_configuration: 'BrowserConfiguration'):
        self.browser_configuration = browser_configuration
        self.explicit: Optional['SearchEngine'] = None
        self.default: Optional['SearchEngine'] = None
        self.private_only = False
        self.hide: list['SearchEngine'] = []
        self.show: list['SearchEngine'] = []

    def get_all(self) -> list['SearchEngine']:
        search_engines = []
        for search_engine in SearchEngine.all.values():
            if self.is_valid(search_engine):
                search_engines.append(search_engine)
        return search_engines

    def is_valid(self, search_engine: 'SearchEngine') -> bool:
        if search_engine in self.show:
            return True
        elif search_engine in self.hide:
            return False
        elif self.private_only and not search_engine.is_private():
            return False
        return True

    def get_search_engine(self, browser: Optional['Browser'] = None) -> 'SearchEngine':
        if self.explicit is not None:
            return self.explicit
        if browser is not None:
            browsers_search_engine = browser.get_search_engine()
        else:
            browsers_search_engine = self.browser_configuration.get_browser().get_search_engine()
        if browsers_search_engine is not None:
            return browsers_search_engine
        return DEFAULT_SEARCH_ENGINE

    def load_args(self, args: Namespace):
        default_search_engine = args.default_search_engine
        if default_search_engine is not None:
            search_engine = SearchEngine.all.get(default_search_engine)
            if search_engine is None:
                raise SearchEngineException(f"No search engine named '{default_search_engine}' found.")
            self.explicit = search_engine


class CustomizationConfig:

    def __init__(self):
        self.aliases_color: Optional[str] = None
        self.kb_browsers: Optional[str] = None
        self.kb_change_language: Optional[str] = None
        self.kb_search_engine: Optional[str] = None
        self.kb_toggle_private: Optional[str] = None
        self.rofi_config: Optional[str] = None
        self.width = 50

    def get_aliases_color(self) -> str:
        if self.aliases_color is None:
            return DEFAULT_ALIASES_COLOR
        return self.aliases_color

    def get_kb_browsers(self) -> Optional[str]:
        return self.kb_browsers

    def get_kb_search_engines(self) -> Optional[str]:
        return self.kb_search_engine

    def get_kb_toggle_private(self) -> Optional[str]:
        return self.kb_toggle_private

    def get_rofi_config(self) -> Optional[str]:
        return self.rofi_config

    def get_width(self) -> int:
        return self.width

class ConfigurationException(Exception):
    pass