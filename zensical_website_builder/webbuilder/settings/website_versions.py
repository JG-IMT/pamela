"""
The versions of a website, as declared in its settings and checked when they are read. The latest is
served at the website URL, each earlier one in a folder named after it - this layout is decided here
only (folder_of, site_url_of); every other class asks.
"""

import re
from collections.abc import Iterator
from urllib.parse import urljoin

VERSION_NAME_PATTERN: re.Pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
VERSION_DECLARATION_KEYS: tuple[str, ...] = ("name", "git_ref", "is_latest", "navigation")


class WebsiteVersion:
    """A version of the documentation: the git reference it is built from, and optionally its own menu."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, declaration: dict) -> None:
        self._check_declaration_keys(declaration)
        self.name: str = self._required_text(declaration, "name")
        self.git_ref: str = self._required_text(declaration, "git_ref")
        self.is_latest: bool = self._optional_boolean(declaration, "is_latest")
        self.navigation: list | None = self._optional_list(declaration, "navigation")
        if not VERSION_NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"version name '{self.name}' may only contain letters, digits, '.', '_' and '-'")


    # -- Private: declaration ------------------------------------------------------------------------

    @staticmethod
    def _check_declaration_keys(declaration) -> None:
        if not isinstance(declaration, dict):
            raise ValueError(f"a version must be 'key: value' lines ({', '.join(VERSION_DECLARATION_KEYS)}), "
                             f"not {declaration!r}")
        unknown_keys: list[str] = [key for key in declaration if key not in VERSION_DECLARATION_KEYS]
        if unknown_keys:
            raise ValueError(f"version {declaration}: unknown key(s) {unknown_keys}, "
                             f"known keys: {', '.join(VERSION_DECLARATION_KEYS)}")


    @staticmethod
    def _required_text(declaration: dict, key: str) -> str:
        value = declaration.get(key)
        if not isinstance(value, str):
            raise ValueError(f"version {declaration}: '{key}' is required and must be text (quote it: \"1.6\")")
        return value


    @staticmethod
    def _optional_boolean(declaration: dict, key: str) -> bool:
        value = declaration.get(key, False)
        if not isinstance(value, bool):
            raise ValueError(f"version {declaration}: '{key}' must be true or false")
        return value


    @staticmethod
    def _optional_list(declaration: dict, key: str) -> list | None:
        value = declaration.get(key)
        if value is not None and not isinstance(value, list):
            raise ValueError(f"version {declaration}: '{key}' must be a list")
        return value


class WebsiteVersions:
    """The versions of a website: the latest is served at the website URL, the others in a folder named after them."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, declared_versions: list[dict], site_url: str) -> None:
        if not isinstance(declared_versions, list):
            raise ValueError("'versions' must be a list of versions")
        self._site_url: str = site_url.rstrip("/") + "/"
        self._versions_in_declared_order: list[WebsiteVersion] = [
            WebsiteVersion(declaration) for declaration in declared_versions
        ]
        self._check_names_are_unique()
        self._check_exactly_one_is_latest()


    # -- Public: the versions ------------------------------------------------------------------------

    def __iter__(self) -> Iterator[WebsiteVersion]:
        return iter(self._versions_in_declared_order)


    @property
    def latest(self) -> WebsiteVersion:
        return next(version for version in self if version.is_latest)


    @property
    def earlier(self) -> list[WebsiteVersion]:
        return [version for version in self if not version.is_latest]


    # -- Public: where a version is in the website ---------------------------------------------------

    def folder_of(self, version: WebsiteVersion) -> str:
        """The folder of the version in the website: "." for the latest, at the root, its name for the others."""
        return "." if version.is_latest else version.name


    def site_url_of(self, version: WebsiteVersion) -> str:
        return urljoin(self._site_url, self.folder_of(version) + "/")


    # -- Private: checks -----------------------------------------------------------------------------

    def _check_names_are_unique(self) -> None:
        names: list[str] = [version.name for version in self]
        if len(set(names)) != len(names):
            raise ValueError("version names must be unique")


    def _check_exactly_one_is_latest(self) -> None:
        latest_versions_count: int = sum(version.is_latest for version in self)
        if latest_versions_count != 1:
            raise ValueError(f"exactly one version must have 'is_latest: true' (found {latest_versions_count})")
