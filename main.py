#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from enum import IntEnum
from locale import locale_alias
from pathlib import Path
from subprocess import CompletedProcess
from typing import Optional, Iterable

from cli import arguments
from config import Configuration, ConfigLocation, GlobalConfigParser, APP_XDG_CONFIG_DIR, APP_DOT_DIR, XDG_CONFIG_DIR, get_user_config
from entries.search_engine import SearchEngine

DEFAULT_ENCODING = "utf-8"
FLAG = object()


class ExitCode(IntEnum):
    SUCCESS = 0
    WRONG_CONFIG_PATH = 1
    INCORRECT_CONFIG = 2
    ROFI_ERROR = 3


def get_rofi_exec() -> list[str]:
    rofi_exec = "rofi"
    if os.getenv("XDG_SESSION_TYPE") == "wayland":
        rofi_exec = "wofi"
    return [rofi_exec, "-dmenu"]


def spawn_rofi(*options, flags: Optional[set[str]] = None, _debug: bool = False, **kwargs) -> CompletedProcess:
    command: list[str] = get_rofi_exec()

    flags = flags if flags is not None else set()
    flags.add("no_sort")
    for flag in flags:
        command.append("-{}".format(flag.replace("_", "-")))

    for k, v in kwargs.items():
        if v is None or (isinstance(v, str) and len(v) == 0):
            continue
        command.append("-{}".format(k.replace("_", "-")))
        if v is not FLAG:
            command.append(str(v))
    stdin = "\n".join(options).encode(DEFAULT_ENCODING)
    if _debug:
        print(subprocess.list2cmdline(command))
    return subprocess.run(command, capture_output=True, input=stdin)


class Application:

    def __init__(self, config: 'Configuration'):
        self.config = config
        self.browser = self.config.browsers.get_browser()
        self.search_engine = self.config.search_engines.get_search_engine()
        self.private = self.config.main.is_private_search_enabled()
        self.language = self.config.main.get_language()
        self.terms = ""

    def handle_return_code(self, return_code: int, current_menu: int = 0) -> 'ExitCode':
        match return_code:
            case 0:
                return self.run()
            case 1:
                if current_menu == 0:
                    return ExitCode.SUCCESS
                return self.run()
            case 10:
                return self.select_browser()
            case 11:
                return self.select_search_engine()
            case 12:
                self.toggle_privacy()
                return self.handle_return_code(current_menu, current_menu)
            case 13:
                return self.select_language()
            case _:
                if 10 <= return_code <= 28:
                    return self.handle_return_code(current_menu, current_menu)
        return ExitCode.ROFI_ERROR

    def make_menu(self, prompt: str, message: str, entries: Optional[Iterable[str]] = None, **kwargs) -> CompletedProcess:
        entries = entries if entries is not None else []
        return spawn_rofi(
            *entries,
            p=prompt,
            mesg=message,
            kb_custom_1=self.config.customization.get_kb_browsers(),
            kb_custom_2=self.config.customization.get_kb_search_engines(),
            kb_custom_3=self.config.customization.get_kb_toggle_private(),
            config=self.config.customization.rofi_config,
            _debug=self.config.debug,
            **kwargs
        )

    def print(self, terms: str, url: str, private: bool):
        column_string = "{:15}{}"
        print(column_string.format("NAME", "VALUE"))
        print(column_string.format("browser", self.browser.get_name()))
        print(column_string.format("search-engine", self.search_engine.get_name()))
        print(column_string.format("language", self.language))
        print(column_string.format("terms", terms))
        print(column_string.format("url", url))
        print(column_string.format("private-search", "yes" if private else "no"))

    def search(self, terms: str):
        url = self.search_engine.format_url(terms, self.language)
        if self.config.debug:
            self.print(terms, url, self.private)
        else:
            self.browser.spawn(url, self.private)

    def select_browser(self) -> 'ExitCode':
        browsers = self.config.browsers.get_all()
        if self.browser in browsers:
            browsers.remove(self.browser)
        process = self.make_menu(
            '',
            f"Your current browser is {self.browser.get_name()}.",
            (b.get_entry(self.config.customization.get_aliases_color()) for b in browsers),
            format='i',
            markup_rows=FLAG
        )
        if process.returncode == 0:
            self.browser = browsers[int(process.stdout.decode(DEFAULT_ENCODING).strip())]
            return self.run()
        return self.handle_return_code(process.returncode, current_menu=10)

    def select_search_engine(self) -> 'ExitCode':
        search_engines = self.config.search_engines.get_all()
        if self.search_engine in search_engines:
            search_engines.remove(self.search_engine)
        process = self.make_menu(
            '󰖟',
            f"Your current search engine is {self.search_engine.get_name()}.",
            (se.get_entry(self.config.customization.get_aliases_color()) for se in search_engines),
            format='i',
            markup_rows=FLAG
        )
        if process.returncode == 0:
            self.search_engine = search_engines[int(process.stdout.decode(DEFAULT_ENCODING).strip())]
            return self.run()
        return self.handle_return_code(process.returncode, current_menu=11)

    def select_language(self) -> 'ExitCode':
        all_languages: set[str] = set()
        for alias in locale_alias.keys():
            lang = alias[:2]
            is_valid = lang.isalpha() and len(lang.lstrip()) == 2
            if lang != self.language and is_valid:
                all_languages.add(lang)
        process = self.make_menu(
            '󰗊',
            f"Your current language is [{self.language}]",
            sorted(all_languages)
        )
        if process.returncode == 0:
            self.language = process.stdout.decode(DEFAULT_ENCODING).strip()
            return self.run()
        return self.handle_return_code(process.returncode, current_menu=13)

    def toggle_privacy(self):
        self.private = not self.private

    def run(self) -> 'ExitCode':
        private_status = " [privately]" if self.private else ""
        process = self.make_menu(
            '',
            f"Search{private_status} on {self.search_engine.get_name()} using {self.browser.get_name()}.",
            filter=self.terms,
            format='s',
            theme_str=f"window {{ width: {self.config.customization.get_width()}%; }} listview {{ enabled: false; }}"
        )
        if process.returncode == 0:
            self.search(process.stdout.decode(DEFAULT_ENCODING).strip())
            return ExitCode.SUCCESS
        elif process.returncode == 1:
            return ExitCode.SUCCESS
        return self.handle_return_code(process.returncode)


def print_browsers(config: 'Configuration') -> 'ExitCode':
    column_string = "{:15}{:15}{:16}{:14}{}"
    print(column_string.format("BROWSER", "EXECUTABLE", "SEARCH-ENGINE", "IS-PRIVATE", "BASE"))
    for browser in config.browsers.get_all():
        print(column_string.format(
            browser.get_name(),
            browser.get_executable(),
            "none" if browser.get_search_engine() is None else browser.get_search_engine().get_name(),
            "yes" if browser.is_private() else "no",
            "yes" if browser.is_installed() else "no",
            browser.get_base().get_name() if browser.get_base() is not None else "none"
        ))
    return ExitCode.SUCCESS


def print_search_engines(config: 'Configuration') -> 'ExitCode':
    column_string = "{:20}{:14}{}"
    print(column_string.format("SEARCH-ENGINE", "IS-PRIVATE", "URL"))
    for name, search_engine in SearchEngine.all.items():
        print(column_string.format(
            name,
            "yes" if search_engine.is_private() else "no",
            search_engine.get_url()
        ))
    return ExitCode.SUCCESS


def copy_default_config(destination: Path) -> 'ExitCode':
    source = Path(os.path.dirname(__file__))
    if destination.exists() and destination.is_file():
        backup = destination.with_suffix(".old.toml")
        shutil.move(destination, backup)
        print(f"Backed up previous config file to {backup}.")
    shutil.copy(source / "default.toml", destination)
    print(f"Initial config file created at {destination}.")
    return ExitCode.SUCCESS


def make_init_config() -> 'ExitCode':
    if XDG_CONFIG_DIR.exists() and XDG_CONFIG_DIR.is_dir():
        if not APP_XDG_CONFIG_DIR.exists() or not APP_XDG_CONFIG_DIR.is_dir():
            APP_XDG_CONFIG_DIR.mkdir()
        return copy_default_config(APP_XDG_CONFIG_DIR / "config.toml")
    if APP_DOT_DIR.exists() and APP_DOT_DIR.is_dir():
        APP_DOT_DIR.mkdir()
    return copy_default_config(APP_DOT_DIR / "config.toml")


def load_config(args: 'Namespace') -> 'Configuration':
    config = Configuration(debug=args.debug)

    # Load user configuration
    user_config = get_user_config()
    if user_config is not None:
        GlobalConfigParser.from_location(config, user_config).load()

    # Load configuration file given through CLI
    if args.configuration_file is not None:
        location = ConfigLocation(Path(args.configuration_file))
        GlobalConfigParser.from_location(config, location).load()

    # Load arguments
    GlobalConfigParser.from_arguments(config, args).load()
    return config


def main(parser: 'ArgumentParser') -> 'ExitCode':
    args, unknown = parser.parse_known_args()
    if len(unknown) != 0:
        print(f"Unknown parameters: {unknown}", file=sys.stderr)

    config = load_config(args)
    if args.list_browsers:
        return print_browsers(config)
    elif args.list_search_engines:
        return print_search_engines(config)
    elif args.make_init_config:
        return make_init_config()

    app = Application(config)
    if args.terms:
        app.search(" ".join(args.terms))
        return ExitCode.SUCCESS
    return app.run()


if __name__ == '__main__':
    sys.exit(main(arguments))