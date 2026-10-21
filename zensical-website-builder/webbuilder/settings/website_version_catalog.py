"""
The versions of a website, as declared in its settings and checked when they are read. The latest version
is served at the website URL, each earlier version in a folder named after it - this layout is decided
here only (folder_of, site_url_of); every other class asks.
"""

from webbuilder.settings.website_version import WebsiteVersion


class WebsiteVersionCatalog:
    """
    All the versions of a website. The latest version (the one declared 'is_latest') is served at the website
    URL, each earlier version in a folder named after it.
    """

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, declared_versions: list[dict], site_url: str) -> None:
        self._site_url: str = site_url.rstrip("/") + "/"  # ends with "/" to add a folder name
        self._versions: list[WebsiteVersion] = self._create_versions(declared_versions)
        self._check_unique_names()
        self._check_latest_version()


    # -- Public: get versions ------------------------------------------------------------------------

    def get_all_versions(self) -> list[WebsiteVersion]:
        """A copy of the list of the versions, in the order they are declared."""
        return list(self._versions)


    def get_latest_version(self) -> WebsiteVersion:
        """The version served at the website URL."""
        for version in self._versions:
            if version.is_latest():
                return version


    def get_earlier_versions(self) -> list[WebsiteVersion]:
        """The versions served in a folder named after them, in the order they are declared."""
        earlier_versions: list[WebsiteVersion] = []
        for version in self._versions:
            if not version.is_latest():
                earlier_versions.append(version)
        return earlier_versions


    # -- Public: where a version is in the website ---------------------------------------------------

    def folder_of(self, version: WebsiteVersion) -> str:
        """The folder of the version in the website: "." for the latest, at the root, its name for the others."""
        return "." if version.is_latest() else version.get_name()


    def site_url_of(self, version: WebsiteVersion) -> str:
        """The address of the version: the website URL for the latest, then the name of the others."""
        if version.is_latest():
            return self._site_url
        return f"{self._site_url}{version.get_name()}/"


    # -- Private: creation ---------------------------------------------------------------------------

    @staticmethod
    def _create_versions(declared_versions: list[dict]) -> list[WebsiteVersion]:
        """Creates one version per declared version. Throws an error if 'versions' is not a list."""
        if not isinstance(declared_versions, list):
            raise ValueError("'versions' must be a list of versions")

        versions: list[WebsiteVersion] = []
        for declared_version in declared_versions:
            versions.append(WebsiteVersion(declared_version))

        return versions


    # -- Private: checks -----------------------------------------------------------------------------

    def _check_unique_names(self) -> None:
        names: list[str] = []
        for version in self._versions:
            names.append(version.get_name())
        if len(set(names)) != len(names):
            raise ValueError("version names must be unique")


    def _check_latest_version(self) -> None:
        latest_versions_count: int = 0
        for version in self._versions:
            if version.is_latest():
                latest_versions_count += 1
        if latest_versions_count != 1:
            raise ValueError(f"exactly one version must have 'is_latest: true' (found {latest_versions_count})")
