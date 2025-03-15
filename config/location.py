from pathlib import Path
from typing import Optional


class ConfigLocation:

    standard_locations: list['ConfigLocation'] = []

    @classmethod
    def get_user_config(cls) -> Optional['ConfigLocation']:
        for location in cls.standard_locations:
            if location.is_valid():
                return location

    @classmethod
    def standard(cls, path: Path) -> 'ConfigLocation':
        location = cls(path)
        cls.standard_locations.append(location)
        return location

    def __init__(self, path: Path):
        self.path = path.resolve()

    def get_config_file(self) -> Path:
        if self.path.is_file():
            return self.path
        elif self.path.is_dir():
            file = self.get_directory_config()
            if file is not None:
                return file
            raise ConfigurationLocationException(f"The directory '{self.path}' does not contain any configuration file.")
        raise ConfigurationLocationException(f"'{self.path}' is neither a file nor a directory.")

    def get_possible_files(self) -> list[Path]:
        return [
            self.path / "config.toml",
            self.path / "rofi-search.toml"
        ]

    def is_valid(self) -> bool:
        if self.path.is_file():
            return True
        elif self.path.is_dir():
            return self.get_directory_config() is not None
        return False

    def get_directory_config(self) -> Optional[Path]:
        for possible_path in self.get_possible_files():
            if possible_path.exists() and possible_path.is_file():
                return possible_path


HOME_DIR = Path.home()
XDG_CONFIG_DIR = HOME_DIR / ".config"

APP_XDG_CONFIG_DIR = ConfigLocation.standard(XDG_CONFIG_DIR / "rofi-search/")
APP_XDG_CONFIG_FILE = ConfigLocation.standard(XDG_CONFIG_DIR / "rofi-search.toml")
APP_DOT_DIR = ConfigLocation.standard(HOME_DIR / ".rofi-search/")
APP_DOT_FILE = ConfigLocation.standard(HOME_DIR / ".rofi-search.toml")


class ConfigurationLocationException(Exception):
    pass