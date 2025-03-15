"""
File containing the definition of a search engine,
as well as some default search engines.

I tried to add support for as many search engines as i could,
but it is not an easy task, so not all of them are present.
If the search engine you need is missing, feel free to edit
your configuration to add it.
A search engine is defined by its (display) name, and its URL.
It also contains some rudimentary metadata, and some details
about how it works. For example:
- if it private or not (if it cares about your privacy)
- a custom field name (most use either 'q' or 'query')
- if it needs to escape the search terms (URL friendly)

There might be some mistakes on which search engines are private
and which are not. If you find anything that doesn't seem normal,
please report it on GitHub.

Please feel free to request any search engine that you would
like to see supported.
"""
import re
from urllib import parse

DEFAULT_SEARCH_FIELD = 'q'

NEEDS_LANGUAGE_REGEX = re.compile(r"^http(s)+://.*(?P<hole>\{lang}).*$")


class SearchEngine:

    all: dict[str, 'SearchEngine'] = {}

    def __new__(cls, name: str, *args, **kwargs):
        obj = super().__new__(cls)
        cls.all[name] = obj
        return obj

    def __init__(self, name: str, url: str, private: bool = False, field: str | None = None, escape: bool = True):
        self.name = name
        self.url = url
        self.private = private
        if field is None:
            self.field = DEFAULT_SEARCH_FIELD
        else:
            self.field = field
        self.escape = escape

    def __str__(self) -> str:
        private_string = ", private" if self.is_private() else ""
        return f'<{self.__class__.__name__} "{self.get_name()}"{private_string}, url="{self.get_url()}">'

    def get_name(self) -> str:
        return self.name

    def get_url(self) -> str:
        return self.url

    def is_private(self) -> bool:
        return self.private

    def search(self, terms: str, lang: str) -> str:
        if len(terms) == 0:
            return self.get_url()

        url = self.get_url()
        if NEEDS_LANGUAGE_REGEX.match(url):
            url = url.format(lang=lang)

        if self.escape:
            query_string = parse.urlencode({self.field: terms})
        else:
            query_string = f"{self.field}={terms}"
        return f"{url}?{query_string}"


class SearchEngineException(Exception):
    pass


AOL = SearchEngine("aol", "https://search.aol.com/aol/search")
ASK = SearchEngine("Ask", "https://www.ask.com/web")
BING = SearchEngine("Bing", "https://www.bing.com/search")
BRAVE_SEARCH = SearchEngine("Brave Search", "https://search.brave.com/search", private=True)
DUCKDUCKGO = SearchEngine("DuckDuckGo", "https://duckduckgo.com/", private=True)
ECOSIA = SearchEngine("Ecosia", "https://www.ecosia.org/search")
GOOGLE = SearchEngine("Google", "https://www.google.com/search")
MOJEEK = SearchEngine("Mojeek", "https://www.mojeek.com/search", private=True)
QWANT = SearchEngine("Qwant", "https://www.qwant.com/", private=True)
STARTPAGE = SearchEngine("Startpage", "https://www.startpage.com/search", private=True)
SWISSCOWS = SearchEngine("Swisscows", "https://swisscows.com/en/web", private=True, field="query")
WAYBACK_MACHINE = SearchEngine("The Wayback Machine", "https://web.archive.org/web/", escape=False)
YAHOO = SearchEngine("Yahoo!", "https://{lang}.search.yahoo.com/search")
YOUTUBE = SearchEngine("YouTube", "https://www.youtube.com/results", field="search_query")