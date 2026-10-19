"""
Reads the settings of one website: the settings shared by every website (shared/site_settings.yml)
completed by the settings of the project (website_settings.yml), and checks them when they are read,
so that a wrong file stops the build with one line naming it. The values Zensical needs stay in
zensical_values; the settings of this tool - the folders to copy, the repository, the versions - are
taken out of them, because Zensical must not receive them.
"""

from pathlib import Path
from urllib.parse import urlparse

import yaml

from webbuilder.settings.website_versions import WebsiteVersions
from webbuilder.shared_files import SHARED_SETTINGS_FILE

SOURCES_KEY: str = "documentation_sources"
REPOSITORY_URL_KEY: str = "repository_url"
VERSIONS_KEY: str = "versions"
NAVIGATION_KEY: str = "nav"


class WebsiteSettings:
    """The settings shared by every website, completed by the settings of one project, and checked."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, project_settings_file: Path) -> None:
        self._project_settings_file: Path = project_settings_file

        shared_settings: dict = self._read_yaml_file(SHARED_SETTINGS_FILE)
        self.zensical_values: dict = self._merge(shared_settings, self._read_project_settings())
        self._check_site_url_is_text()
        self._check_extra_is_a_mapping()
        self._check_no_global_navigation()

        self.sources: list[dict] = self._pop_required_from_extra(SOURCES_KEY, "folders to copy")
        self._check_sources_have_source_and_destination()
        self._repository_url: str | None = self.zensical_values["extra"].pop(REPOSITORY_URL_KEY, None)  # "build" only
        declared_versions: list[dict] = self._pop_required_from_extra(VERSIONS_KEY, "versions to build")
        self.versions: WebsiteVersions = self._create_versions(declared_versions)


    # -- Public: settings ----------------------------------------------------------------------------

    @property
    def project_url_path(self) -> str:
        """The project path in URLs, from "homepage": https://openflexo.org/my_project/ gives "my_project"."""
        homepage_url: str = self.zensical_values["extra"].get("homepage", "")
        return urlparse(homepage_url).path.strip("/")


    def repository_url_to_clone(self, override_url: str | None) -> str:
        """The repository to clone: the one given on the command line, else the one of the settings."""
        repository_url: str | None = override_url or self._repository_url
        if not repository_url:
            raise SystemExit(f"{self._project_settings_file}: no '{REPOSITORY_URL_KEY}' under 'extra:' "
                             "(repository to clone), and no --repository-url given")
        return repository_url


    # -- Private: reading ----------------------------------------------------------------------------

    def _read_project_settings(self) -> dict:
        project_settings = self._read_yaml_file(self._project_settings_file)
        if not isinstance(project_settings, dict):
            raise SystemExit(f"{self._project_settings_file}: no settings (the file is empty or has no 'key: value')")
        return project_settings


    @staticmethod
    def _read_yaml_file(file: Path):
        try:
            return yaml.safe_load(file.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise SystemExit(f"{file}: not valid YAML ({error})")


    @staticmethod
    def _merge(shared: dict, project: dict) -> dict:
        """The project wins; nested sections are merged key by key, lists are replaced."""
        merged: dict = dict(shared)
        for key, project_value in project.items():
            shared_value = shared.get(key)
            if isinstance(shared_value, dict) and isinstance(project_value, dict):
                merged[key] = WebsiteSettings._merge(shared_value, project_value)
            else:
                merged[key] = project_value
        return merged


    # -- Private: the settings of this tool ----------------------------------------------------------

    def _pop_required_from_extra(self, key: str, purpose: str):
        """Removes the key from the values: Zensical must not receive the settings of this tool."""
        extra: dict = self.zensical_values["extra"]
        if key not in extra:
            raise SystemExit(f"{self._project_settings_file}: no '{key}' under 'extra:' ({purpose})")
        return extra.pop(key)


    def _create_versions(self, declared_versions: list[dict]) -> WebsiteVersions:
        try:
            return WebsiteVersions(declared_versions, self.zensical_values["site_url"])
        except ValueError as error:
            raise SystemExit(f"{self._project_settings_file}: {error}")


    # -- Private: checks -----------------------------------------------------------------------------

    def _check_site_url_is_text(self) -> None:
        if not isinstance(self.zensical_values.get("site_url"), str):
            raise SystemExit(f"{self._project_settings_file}: 'site_url' is required and must be text")


    def _check_extra_is_a_mapping(self) -> None:
        if not isinstance(self.zensical_values.get("extra"), dict):
            raise SystemExit(f"{self._project_settings_file}: 'extra' must contain 'key: value' lines")


    def _check_no_global_navigation(self) -> None:
        if NAVIGATION_KEY in self.zensical_values:
            raise SystemExit(f"{self._project_settings_file}: '{NAVIGATION_KEY}' would apply to every version; "
                             "put it in 'navigation' of the version it belongs to")


    def _check_sources_have_source_and_destination(self) -> None:
        if not isinstance(self.sources, list) or not all(self._has_source_and_destination(entry)
                                                         for entry in self.sources):
            raise SystemExit(f"{self._project_settings_file}: '{SOURCES_KEY}' must be a list of entries "
                             "with a 'source' and a 'destination' folder")


    @staticmethod
    def _has_source_and_destination(entry) -> bool:
        return isinstance(entry, dict) and isinstance(entry.get("source"), str) \
            and isinstance(entry.get("destination"), str)
