"""
Reads the settings of one website: the settings shared by every website (shared/default_settings.yml)
completed by the settings of the project (website_settings.yml), and checks them when they are read,
so that a wrong file stops the build with one line naming it.
"""

import copy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from webbuilder.settings.website_version_catalog import WebsiteVersionCatalog
from webbuilder.shared_paths import DEFAULT_SETTINGS_FILE

DOCUMENTATION_SOURCES_KEY: str = "documentation_sources"
REPOSITORY_URL_KEY: str = "repository_url"
VERSIONS_KEY: str = "versions"
NAVIGATION_KEY: str = "nav"


class WebsiteSettings:
    """Reads the settings shared by every website and completes them by the settings of one project."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, project_settings_file: Path) -> None:
        self._project_settings_file: Path = project_settings_file

        # What Zensical receives: the default settings overridden by the project settings.
        default_settings: dict = self._read_settings_file(DEFAULT_SETTINGS_FILE)
        project_settings: dict = self._read_settings_file(self._project_settings_file)
        self._zensical_settings: dict = self._merge_settings(default_settings, project_settings)
        self._check_zensical_settings()

        # What only the website builder needs (not Zensical): taken out of the settings above.
        self._documentation_sources: list[dict] = self._extract_documentation_sources()
        self._repository_url: str = self._extract_repository_url()
        self._version_catalog: WebsiteVersionCatalog = self._extract_version_catalog()


    # -- Public: get settings ------------------------------------------------------------------------

    def get_zensical_settings(self) -> dict:
        """
        A copy of the settings Zensical receives: the default settings overridden by the project settings,
        without the ones only the website builder needs (documentation sources, repository URL, versions).
        """
        return copy.deepcopy(self._zensical_settings)


    def get_documentation_sources(self) -> list[dict]:
        """A copy of the folders of the repository to copy into the website, each with its 'source' and 'destination'."""
        return copy.deepcopy(self._documentation_sources)


    def get_repository_url(self) -> str:
        """The git repository the versions are cloned from."""
        return self._repository_url


    def get_version_catalog(self) -> WebsiteVersionCatalog:
        """The versions of the website, and where each one is in the website."""
        return self._version_catalog


    def get_project_url_path(self) -> str:
        """The project path in URLs, from "homepage": https://openflexo.org/my_project/ gives "my_project"."""
        homepage_url: str = self._zensical_settings["extra"].get("homepage", "")
        return urlparse(homepage_url).path.strip("/")


    # -- Private: reading ----------------------------------------------------------------------------

    @staticmethod
    def _read_settings_file(file: Path) -> dict:
        """Reads a settings file. Throw an error if it is not valid YAML or has no 'key: value' settings."""
        try:
            file_settings: object = yaml.safe_load(file.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise SystemExit(f"{file}: not valid YAML ({error})")
        if not isinstance(file_settings, dict):
            raise SystemExit(f"{file}: no settings (the file is empty or has no 'key: value')")
        return file_settings


    @staticmethod
    def _merge_settings(default_settings: dict, project_settings: dict) -> dict:
        """Overrides default settings with project settings, key by key."""
        merged_settings: dict = dict(default_settings)
        for key, project_value in project_settings.items():
            default_value: object = default_settings.get(key)
            if isinstance(default_value, dict) and isinstance(project_value, dict):
                merged_settings[key] = WebsiteSettings._merge_settings(default_value, project_value)
            else:
                merged_settings[key] = project_value
        return merged_settings


    # -- Private: website builder settings -----------------------------------------------------------

    def _extract_documentation_sources(self) -> list[dict]:
        """The folders of the repository to copy into the website, each with its 'source' and 'destination'."""
        documentation_sources: list[dict] = self._extract_key_from_extra(
            DOCUMENTATION_SOURCES_KEY, "folders to copy"
        )
        self._check_documentation_sources(documentation_sources)
        return documentation_sources


    def _extract_repository_url(self) -> str:
        """The git repository the versions are cloned from."""
        return self._extract_key_from_extra(REPOSITORY_URL_KEY, "repository to clone")


    def _extract_version_catalog(self) -> WebsiteVersionCatalog:
        """The catalog of versions to build: names, git references, which one is the latest version."""
        declared_versions: list[dict] = self._extract_key_from_extra(VERSIONS_KEY, "versions to build")
        try:
            return WebsiteVersionCatalog(declared_versions, self._zensical_settings["site_url"])
        except ValueError as error:
            raise SystemExit(f"{self._project_settings_file}: {error}")


    def _extract_key_from_extra(self, key: str, purpose: str) -> Any:
        """Removes the key from 'extra' and returns its value. Throws an error if the key is missing."""
        extra: dict = self._zensical_settings["extra"]
        if key not in extra:
            raise SystemExit(f"{self._project_settings_file}: no '{key}' under 'extra:' ({purpose})")
        return extra.pop(key)


    # -- Private: input verification -----------------------------------------------------------------

    def _check_zensical_settings(self) -> None:
        self._check_site_url()
        self._check_extra()
        self._check_no_global_navigation()


    def _check_site_url(self) -> None:
        if not isinstance(self._zensical_settings.get("site_url"), str):
            raise SystemExit(f"{self._project_settings_file}: 'site_url' is required and must be text")


    def _check_extra(self) -> None:
        if not isinstance(self._zensical_settings.get("extra"), dict):
            raise SystemExit(f"{self._project_settings_file}: 'extra' must contain 'key: value' lines")


    def _check_no_global_navigation(self) -> None:
        if NAVIGATION_KEY in self._zensical_settings:
            raise SystemExit(f"{self._project_settings_file}: '{NAVIGATION_KEY}' would apply to every version; "
                             "put it in 'navigation' of the version it belongs to")


    def _check_documentation_sources(self, documentation_sources: list[dict]) -> None:
        is_valid: bool = isinstance(documentation_sources, list)
        if is_valid:
            for documentation_source in documentation_sources:
                if not self._has_source_and_destination(documentation_source):
                    is_valid = False
        if not is_valid:
            raise SystemExit(f"{self._project_settings_file}: '{DOCUMENTATION_SOURCES_KEY}' must be a list of entries "
                             "with a 'source' and a 'destination' folder")


    @staticmethod
    def _has_source_and_destination(entry: object) -> bool:
        return isinstance(entry, dict) and isinstance(entry.get("source"), str) and isinstance(entry.get("destination"), str)
