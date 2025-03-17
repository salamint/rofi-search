from argparse import ArgumentParser
from pathlib import Path

from entries.browser import Browser
from entries.search_engine import SearchEngine

browser_names = sorted(Browser.all.keys())
search_engine_names = sorted(SearchEngine.all.keys())

# Main options
arguments = ArgumentParser("rofi-search")
arguments.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
arguments.add_argument("--terms", "-t", nargs="+")
arguments.add_argument(
    "--configuration-file", "--configuration", "--config", "--config-file", "-c",
    type=Path,
    help="Path to the TOML configuration file."
)
arguments.add_argument(
    "--debug", "--fake-run", "-d",
    action="store_true",
    help="Prints the Browser to be opened and the URL to open then exits."
)
arguments.add_argument(
    "--language", "--locale", "--lang",
    help="Sets the language or locale tu use with the search engine."
)
arguments.add_argument(
    "--list-browsers",
    action="store_true",
    help="Lists all the supported browsers."
)
arguments.add_argument(
    "--list-search-engines",
    action="store_true",
    help="Lists all the supported search engines."
)
arguments.add_argument(
    "--private-search", "--private", "-p",
    action="store_true",
    help="Opens the link in a private tab/window."
)
arguments.add_argument(
    "--make-init-config", "--init-config", "--init",
    action="store_true",
    help="Creates a new (commented) configuration file in the user's configuration directory. Recommended for first time users."
)
arguments.add_subparsers()

# Browser options
browser = arguments.add_argument_group("browser")
browser.add_argument(
    "--preferred-browsers", "--preferred-browser", "--browsers", "--browser", "-b",
    choices=browser_names,
    nargs='+',
    help="Sets the preferred browser(s) to use (comma separated)."
)
browser.add_argument(
    "--private-browsers-only", "--private-browsers", "-B",
    action="store_true",
    default=None,
    help="Filters to show only browsers that respects your privacy."
)
browser.add_argument(
    "--show-browsers",
    choices=browser_names,
    nargs='+',
    help="Shows the given browsers (comma separated). Overrides all other options."
)
browser.add_argument(
    "--hide-browsers",
    choices=browser_names,
    nargs='+',
    help="Hides the given browsers (comma separated). Overrides all other options."
)
browser.add_argument(
    "--show-browsers-based-on", "--show-based-on", "--show-based",
    choices=browser_names,
    nargs='+',
    help="Show the browsers based on a certain browser."
)
browser.add_argument(
    "--hide-browsers-based-on", "--hide-based-on", "--hide-based",
    choices=browser_names,
    nargs='+',
    help="Hides the browsers based on a certain browser."
)

# Search engine options
search_engine = arguments.add_argument_group("search engine")
search_engine.add_argument(
    "--default-search-engine", "--search-engine", "-s",
    choices=search_engine_names,
    help="Sets the default search engine to use."
)
search_engine.add_argument(
    "--private-search-engine-only", "--private-search-engines", "-S",
    action="store_true",
    default=None,
    help="Filters to show only search engines that respects your privacy."
)
search_engine.add_argument(
    "--hide-search-engines",
    choices=search_engine_names,
    nargs='+',
    help="Hides the given search engines (comma separated). Overrides all other options."
)
search_engine.add_argument(
    "--show-search-engines",
    choices=search_engine_names,
    nargs='+',
    help="Shows the given search engines (comma separated). Overrides all other options."
)

# Customization
customization = arguments.add_argument_group("customization")
customization.add_argument("--aliases-color", help="Sets to use for aliases in pango color format (hex or color name).")
customization.add_argument("--kb-browsers", help="Sets the keybinding to open the browser list.")
customization.add_argument("--kb-change-language", help="Sets the keybinding to open the language list.")
customization.add_argument("--kb-search-engines", help="Sets the keybinding to open the search engine list.")
customization.add_argument("--kb-toggle-private-search", "--kb-toggle-private", help="Sets the keybinding to toggle the private search..")
customization.add_argument("--rofi-config", help="Path to a rofi configuration file to use instead of the default one.")
customization.add_argument("--width", "-w", type=int, help="Sets the width of the search bar (in %% of display width).")