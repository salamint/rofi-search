from typing import Optional


class Entry:
    
    def __init__(self, name: str, utility: str, aliases: Optional[list[str]] = None):
        self.name = name
        self.utility = utility
        self.aliases = aliases if aliases is not None else []

    def get_aliases(self) -> list[str]:
        return self.aliases

    def get_entry(self, aliases_color: str) -> str:
        return f'{self.get_name()} <span color="{aliases_color}">{" ".join(self.get_aliases())}</span>'

    def get_name(self) -> str:
        return self.name