# rofi-search

This Python script allows you to make online searches from a rofi menu.
This script permits you to pick your preferred browser(s), and your default search engine.
It is configurable through a configuration file, and you can add/edit support to any browser or search engine you want.

## Dependencies

- [Python 3.12](https://www.python.org/downloads/) or higher
- [rofi](https://github.com/davatorium/rofi/releases)

## Usage
```
usage: rofi-search [-h] [--version] [--terms TERMS [TERMS ...]]
                   [--configuration-file CONFIGURATION_FILE] [--debug]
                   [--language LANGUAGE] [--list-browsers]
                   [--list-search-engines] [--private-search]
                   [--make-init-config]
                   [--preferred-browsers {...} [{...} ...]]
                   [--private-browsers-only]
                   [--show-browsers {...} [{...} ...]]
                   [--hide-browsers {...} [{...} ...]]
                   [--show-browsers-based-on {...} [{...} ...]]
                   [--hide-browsers-based-on {...} [{...} ...]]
                   [--default-search-engine {...}]
                   [--private-search-engine-only]
                   [--hide-search-engines {...} [{...} ...]]
                   [--show-search-engines {...} [{...} ...]]
                   [--aliases-color ALIASES_COLOR] [--kb-browsers KB_BROWSERS]
                   [--kb-change-language KB_CHANGE_LANGUAGE]
                   [--kb-search-engines KB_SEARCH_ENGINES]
                   [--kb-toggle-private-search KB_TOGGLE_PRIVATE_SEARCH]
                   [--rofi-config ROFI_CONFIG] [--width WIDTH]
                   {} ...

positional arguments:
  {}

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --terms, -t TERMS [TERMS ...]
  --configuration-file, --configuration, --config, --config-file, -c CONFIGURATION_FILE
                        Path to the TOML configuration file.
  --debug, --fake-run, -d
                        Prints the Browser to be opened and the URL to open
                        then exits.
  --language, --locale, --lang LANGUAGE
                        Sets the language or locale tu use with the search
                        engine.
  --list-browsers       Lists all the supported browsers.
  --list-search-engines
                        Lists all the supported search engines.
  --private-search, --private, -p
                        Opens the link in a private tab/window.
  --make-init-config, --init-config, --init
                        Creates a new (commented) configuration file in the
                        user's configuration directory. Recommended for first
                        time users.

browser:
  --preferred-browsers, --preferred-browser, --browsers, --browser, -b {...} [{...} ...]
                        Sets the preferred browser(s) to use (comma
                        separated).
  --private-browsers-only, --private-browsers, -B
                        Filters to show only browsers that respects your
                        privacy.
  --show-browsers {...} [{...} ...]
                        Shows the given browsers (comma separated). Overrides
                        all other options.
  --hide-browsers {...} [{...} ...]
                        Hides the given browsers (comma separated). Overrides
                        all other options.
  --show-browsers-based-on, --show-based-on, --show-based {...} [{...} ...]
                        Show the browsers based on a certain browser.
  --hide-browsers-based-on, --hide-based-on, --hide-based {...} [{...} ...]
                        Hides the browsers based on a certain browser.

search engine:
  --default-search-engine, --search-engine, -s {...}
                        Sets the default search engine to use.
  --private-search-engine-only, --private-search-engines, -S
                        Filters to show only search engines that respects your
                        privacy.
  --hide-search-engines {...} [{...} ...]
                        Hides the given search engines (comma separated).
                        Overrides all other options.
  --show-search-engines {...} [{...} ...]
                        Shows the given search engines (comma separated).
                        Overrides all other options.

customization:
  --aliases-color ALIASES_COLOR
                        Sets to use for aliases in pango color format (hex or
                        color name).
  --kb-browsers KB_BROWSERS
                        Sets the keybinding to open the browser list.
  --kb-change-language KB_CHANGE_LANGUAGE
                        Sets the keybinding to open the language list.
  --kb-search-engines KB_SEARCH_ENGINES
                        Sets the keybinding to open the search engine list.
  --kb-toggle-private-search, --kb-toggle-private KB_TOGGLE_PRIVATE_SEARCH
                        Sets the keybinding to toggle the private search..
  --rofi-config ROFI_CONFIG
                        Path to a rofi configuration file to use instead of
                        the default one.
  --width, -w WIDTH     Sets the width of the search bar (in % of display
                        width).
```

### Getting help
```shell
rofi-search --help
```

### Listing installed browsers
```shell
rofi-search --list-browsers
```

### Debugging / fake running
```shell
rofi-search --debug
```

### Creating a new configuration file
```shell
rofi-search --make-init-config
```
Will try the following location:
- `~/.config/rofi-search/config.toml` if `~/.config` exists
- `~/.rofi-search/config.toml`

Will backup you previous config file by renaming it to `config.old.toml`.
It **WILL NOT BACKUP** any file named `config.old.toml`.

### Searching without opening the rofi menu
```shell
rofi-search --terms <terms>
```

## Configuration

rofi-search will check for these files:
1. `~/.config/rofi-search/config.toml`
2. `~/.config/rofi-search/rofi-search.toml`
3. `~/.config/rofi-search.toml`
4. `~/.rofi-search/config.toml`
5. `~/.rofi-search/rofi-search.toml`
6. `~/.rofi-search.toml`

For more detailed configuration, read `default.toml`.

## Browsers and search engines support

All browsers and search engines are not currently tested.
Testing will come when I have more time.

If you want to edit/add support for a browser/search engine you are using,
you can do it using the configuration file.