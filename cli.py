from argparse import ArgumentParser
from pathlib import Path

# Main options
arguments = ArgumentParser("rofi-search")
arguments.add_argument("terms", nargs='*')
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
    "--list-browsers", "--list", "-l",
    action="store_true",
    help="Lists all the currently available (installed) browsers on your machine."
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
    help="Sets the preferred browser(s) to use (comma separated)."
)
browser.add_argument(
    "--private-browsers-only", "--private-browsers", "-B",
    action="store_true",
    help="Filters to show only browsers that respects your privacy."
)
browser.add_argument("--show-browsers", help="Shows the given browsers (comma separated). Overrides all other options.")
browser.add_argument("--hide-browsers", help="Hides the given browsers (comma separated). Overrides all other options.")
browser.add_argument(
    "--show-browsers-based-on", "--show-based-on", "--show-based",
    help="Show the browsers based on a certain browser."
)
browser.add_argument(
    "--hide-browsers-based-on", "--hide-based-on", "--hide-based",
    help="Hides the browsers based on a certain browser."
)

# Search engine options
search_engine = arguments.add_argument_group("search engine")
search_engine.add_argument(
    "--default-search-engine", "--search-etngine", "-s",
    help="Sets the default search engine to use."
)
search_engine.add_argument(
    "--private-search-engine-only", "--private-search-engines", "-S",
    action="store_true",
    help="Filters to show only search engines that respects your privacy."
)
search_engine.add_argument("--hide-search-engines", help="Hides the given search engines (comma separated). Overrides all other options.")
search_engine.add_argument("--show-search-engines", help="Shows the given search engines (comma separated). Overrides all other options.")

# Customization
customization = arguments.add_argument_group("customization")
customization.add_argument("--kb-browsers", help="Sets the keybinding to open the browser list.")
customization.add_argument("--kb-change-language", help="Sets the keybinding to open the language list.")
customization.add_argument("--kb-search-engines", help="Sets the keybinding to open the search engine list.")
customization.add_argument("--kb-toggle-private-search", "--kb-toggle-private", help="Sets the keybinding to toggle the private search..")
customization.add_argument("--width", "-w", type=int, help="Sets the width of the search bar (in %% of display width).")