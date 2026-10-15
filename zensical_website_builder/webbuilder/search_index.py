import json
import posixpath
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SEARCH_INDEX_FILE_NAME: str = "search.json"
DOWNLOAD_TIMEOUT_SECONDS: int = 10


class SearchIndex:
    """The search.json of a built website, which can also hold the pages of other websites."""

    def __init__(self, index_file: Path, own_site_url: str):
        self.index_file: Path = index_file
        self.own_site_url: str = own_site_url
        self.content: dict = json.loads(index_file.read_text(encoding="utf-8"))

    # -- Public: entry point ------------------------------------------------------------

    def add_other_websites(self, other_websites: list) -> int:
        added_entries_count: int = 0
        for other_website in other_websites:
            entries: list = self._download_entries(other_website)
            self.content["items"].extend(entries)
            added_entries_count += len(entries)
        return added_entries_count

    def save(self) -> None:
        self.index_file.write_text(json.dumps(self.content, ensure_ascii=False), encoding="utf-8")

    # -- Private: other websites --------------------------------------------------------

    def _download_entries(self, other_website: dict) -> list:
        """Entries of another website, with links relative to this website and titles prefixed by its name."""
        other_site_url: str = other_website["site_url"].rstrip("/") + "/"
        try:
            path_to_other_website: str = self._relative_path_to(other_site_url)
            with urllib.request.urlopen(other_site_url + SEARCH_INDEX_FILE_NAME,
                                        timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                other_entries: list = json.load(response)["items"]
        except (OSError, ValueError, KeyError) as error:
            print(f"Warning: search index of {other_website['name']} ignored ({error})")
            return []

        global_entries: list = []
        for other_entry in other_entries:
            global_entries.append(self._to_global_entry(other_entry, other_website["name"], path_to_other_website))
        return global_entries

    def _relative_path_to(self, other_site_url: str) -> str:
        """Search results are opened relative to the website: the other website must share its domain."""
        own_url = urlparse(self.own_site_url)
        other_url = urlparse(other_site_url)
        if (own_url.scheme, own_url.netloc) != (other_url.scheme, other_url.netloc):
            raise ValueError(f"{other_site_url} is not on the same domain as {self.own_site_url}")
        return posixpath.relpath(other_url.path, own_url.path) + "/"

    # -- Private: entries ---------------------------------------------------------------

    @staticmethod
    def _to_global_entry(entry: dict, website_name: str, path_to_other_website: str) -> dict:
        return {**entry, "location": path_to_other_website + entry["location"],
                "title": f"{website_name} › {entry['title']}"}
