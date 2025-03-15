import pprint
import tomllib
from argparse import Namespace
from pathlib import Path
from typing import Any, Callable, Optional

from browser import Browser
from search_engine import SearchEngine

from .config import Configuration
from .location import ConfigLocation


Section = dict[str, Any]
SimpleMethod = Callable[['ConfigParser'], Any]


class MetaConfigParser(type):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.section: Optional[str] = None


class ConfigParser(metaclass=MetaConfigParser):

    def __init__(self, config, data: Section):
        self.config = config
        self.data = data

    def load(self):
        for attr in dir(self):
            loader = getattr(self, attr)
            if attr.startswith("load_") and callable(loader):
                loader()
        post_parsing = getattr(self, "post_parsing", None)
        if post_parsing is not None and callable(post_parsing):
            post_parsing()


def section_parser(section: str):
    def decorator(cls: type) -> type:
        cls.section = section
        return cls
    return decorator


def setting_parser(setting: str, type_: type) -> Callable[[Callable[['ConfigParser', Any], Any]], callable]:
    def decorator(method: Callable[[ConfigParser, Any], Any]) -> Callable[[ConfigParser], Any]:
        def loader_method(self: 'ConfigParser'):
            data = self.data.get(setting)
            if data is None:
                return
            elif not isinstance(data, type_):
                raise IncorrectTypeConfigException(self.__class__.section, setting, type_)
            return method(self, data)
        return loader_method
    return decorator


class GlobalConfigParser(ConfigParser):

    parsed: list[Path] = []

    @classmethod
    def from_location(cls, config: 'Configuration', location: 'ConfigLocation') -> Optional['GlobalConfigParser']:
        file = location.get_config_file()
        if config.has_loaded(file):
            return None

        with location.get_config_file().open("rb") as f:
            data = tomllib.load(f)
            return cls(config, data)

    @classmethod
    def from_arguments(cls, config: 'Configuration', args: 'Namespace'):
        data = {
            "main": {
                "lang": args.language,
                "private_search": args.private_search
            },
            "browsers": {
                "preferred": args.preferred_browsers,
                "private_only": args.private_browsers_only,
                "hide": args.hide_browsers,
                "show": args.show_browsers,
                "hide_based_on": args.hide_browsers_based_on,
                "show_based_on": args.show_browsers_based_on
            },
            "search_engines": {
                "default": args.default_search_engine,
                "private_only": args.private_search_engine_only,
                "hide": args.hide_search_engines,
                "show": args.show_search_engines
            },
            "customization": {
                "kb_browsers": args.kb_browsers,
                "kb_change_language": args.kb_change_language,
                "kb_search_engines": args.kb_search_engines,
                "kb_toggle_private_search": args.kb_toggle_private_search,
                "width": args.width
            }
        }

        empty_sections: list[str] = []
        for name, section in data.items():
            unset: list[str] = []
            for setting, value in section.items():
                if value is None:
                    unset.append(setting)
            for key in unset:
                section.pop(key)
            if len(section) == 0:
                empty_sections.append(name)
        for section in empty_sections:
            data.pop(section)
        return cls(config, data)

    def __init__(self, config: 'Configuration', data: Section):
        super().__init__(config, data)
        self.sources: list[Path] = []

    def internal_load_section(self, parser: MetaConfigParser):
        section = self.data.get(parser.section)
        if section is None:
            return
        elif not isinstance(section, dict):
            raise MustBeSectionException(parser.section)
        config_parser = parser(getattr(self.config, parser.section), section)
        config_parser.load()

    def load_sections(self):
        self.internal_load_section(MainConfigParser)
        self.internal_load_section(BrowsersConfigParser)
        self.internal_load_section(SearchEnginesConfigParser)
        self.internal_load_section(CustomizationConfigParser)

    @setting_parser("browser", dict)
    def load_custom_browsers(self, custom_browsers_section: dict[str, dict[str, Any]]):
        for name, settings in custom_browsers_section.items():
            base_name = settings.get("base")
            if base_name is not None or base_name != "":
                base = Browser.all.get(base_name)
                if base is None:
                    raise ConfigParsingException(f"browser.{name}", f"'{base_name}' is not a browser name.")
            else:
                base = None
            Browser(
                name,
                arguments=settings["arguments"],
                private=settings.get("private", False),
                base=base
            )

    @setting_parser("search_engine", dict)
    def load_custom_search_engines(self, custom_search_engines_section: dict[str, dict[str, Any]]):
        for name, settings in custom_search_engines_section.items():
            SearchEngine(
                name,
                url=settings["url"],
                private=settings.get("private", False),
                escape=settings.get("escape", False)
            )

    def post_parsing(self):
        for source in self.config.main.sources:
            location = ConfigLocation(source)
            path = location.get_config_file()
            if path in GlobalConfigParser.parsed:
                continue
            if self.config.debug:
                print("Loading config file:", path)
            parser = GlobalConfigParser.from_location(self.config, location)
            if parser is not None:
                GlobalConfigParser.parsed.append(path)
                parser.load()


@section_parser("main")
class MainConfigParser(ConfigParser):

    @setting_parser("lang", str)
    def load_language(self, lang: str):
        self.config.language = lang

    @setting_parser("private_search", bool)
    def load_private_search(self, private_search: bool):
        self.config.private_search = private_search

    @setting_parser("sources", list)
    def load_sources(self, sources: list[str]):
        sources_paths: list[Path] = []
        for source in sources:
            if not isinstance(source, str):
                raise ConfigParsingException(self.section, "Every source must be of type string representing a path.")
            sources_paths.append(Path(source).expanduser())
        self.config.sources = sources_paths


@section_parser("browsers")
class BrowsersConfigParser(ConfigParser):

    @classmethod
    def get_browsers_from_names(cls, names: list[str]) -> list['Browser']:
        browsers: list['Browser'] = []
        for name in names:
            browser = Browser.all.get(name)
            if browser is None:
                raise ConfigParsingException(cls.section, f"'{name}' is not the name os a web browser.")
            browsers.append(browser)
        return browsers

    @setting_parser("preferred", list)
    def load_preferred(self, preferred: list[str]):
        self.config.preferred = self.get_browsers_from_names(preferred)

    @setting_parser("private_only", bool)
    def load_private_only(self, private_only: bool):
        self.config.private_only = private_only

    @setting_parser("hide", list)
    def load_hidden(self, hide: list[str]):
        self.config.hide = self.get_browsers_from_names(hide)

    @setting_parser("show", list)
    def load_shown(self, show: list[str]):
        self.config.show = self.get_browsers_from_names(show)

    @setting_parser("hide_based_on", list)
    def load_hidden_based_on(self, hide_based_on: list[str]):
        self.config.hide_based_on = self.get_browsers_from_names(hide_based_on)

    @setting_parser("show_based_on", list)
    def load_shown_based_on(self, show_based_on: list[str]):
        self.config.show_based_on = self.get_browsers_from_names(show_based_on)


@section_parser("search_engines")
class SearchEnginesConfigParser(ConfigParser):

    @classmethod
    def get_search_engines_from_names(cls, names: list[str]) -> list['SearchEngine']:
        search_engines: list['SearchEngine'] = []
        for name in names:
            search_engine = SearchEngine.all.get(name)
            if search_engine is None:
                raise ConfigParsingException(cls.section, f"'{name}' is not the name of a search engine.")
            search_engines.append(search_engine)
        return search_engines

    @setting_parser("default", str)
    def load_default(self, default: str):
        search_engine = SearchEngine.all.get(default)
        if search_engine is None:
            raise ConfigParsingException(self.section, "No search engine named '{default}' was found.")
        self.config.default = default

    @setting_parser("private_only", bool)
    def load_private_only(self, private_only: bool):
        self.config.private_only = private_only

    @setting_parser("hide", list)
    def load_hidden(self, hide: list[str]):
        self.config.hide = self.get_search_engines_from_names(hide)

    @setting_parser("show", list)
    def load_shown(self, show: list[str]):
        self.config.show = self.get_search_engines_from_names(show)


@section_parser("customization")
class CustomizationConfigParser(ConfigParser):

    @setting_parser("kb_browsers", str)
    def load_kb_browsers(self, kb_browsers: str):
        self.config.kb_browsers = kb_browsers

    @setting_parser("kb_change_language", str)
    def load_kb_change_language(self, kb_change_language: str):
        self.config.kb_change_language = kb_change_language

    @setting_parser("kb_search_engines", str)
    def load_kb_search_engines(self, kb_search_engines: str):
        self.config.kb_search_engine = kb_search_engines

    @setting_parser("kb_toggle_private_search", str)
    def load_kb_toggle_private_search(self, kb_toggle_private_search: str):
        self.config.kb_toggle_private = kb_toggle_private_search

    @setting_parser("width", int)
    def load_width(self, width: int):
        if not isinstance(width, int):
            raise IncorrectTypeConfigException("customization", "width", int)
        if not 0 < width <= 100:
            raise ConfigParsingException(self.section, "Width must be greater than 0% and has a maximum value of 100%.")
        self.config.width = width


class ConfigParsingException(Exception):

    def __init__(self, section: str, message: str):
        self.section = section
        self.message = message

    def __str__(self) -> str:
        return self.message


class IncorrectTypeConfigException(ConfigParsingException):

    def __init__(self, section: Optional[str], setting: str, type_: type):
        section_string = f"{self.section}." if self.section is not None else ""
        super().__init__(section, f"Setting '{section_string}{setting}' must be of type '{type.__name__}'.")
        self.setting = setting
        self.type = type_


class MustBeSectionException(ConfigParsingException):

    def __init__(self, name: str):
        super().__init__(name, f"'{name}' is supposed to be a section, not a variable.")