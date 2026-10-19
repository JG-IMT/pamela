from pathlib import Path
from urllib.parse import urlparse

import yaml

from webbuilder.website_version import WebsiteVersion


TOOL_FOLDER: Path = Path(__file__).parent.parent
SHARED_FOLDER: Path = TOOL_FOLDER / "shared"
SHARED_SETTINGS_FILE: Path = SHARED_FOLDER / "site_settings.yml"
SHARED_STYLE_AND_ICON_FOLDER: Path = SHARED_FOLDER / "style_and_icon"
SHARED_HTML_TEMPLATES_FOLDER: Path = SHARED_FOLDER / "html_templates"

SOURCES_KEY: str = "documentation_sources"
REPOSITORY_URL_KEY: str = "repository_url"
VERSIONS_KEY: str = "versions"
GLOBAL_SEARCH_KEY: str = "global_search"
NAVIGATION_KEY: str = "nav"


class WebsiteSettings:
    """The settings shared by every website, completed by the settings of one project."""

    def __init__(self, project_settings_file: Path):
        self.project_settings_file: Path = project_settings_file
        self.values: dict = self._merge(read_yaml(SHARED_SETTINGS_FILE), read_yaml(project_settings_file))
        self._check_no_global_navigation()
        self.sources: list = self._extract_required_from_extra(SOURCES_KEY, "folders to copy")
        self.repository_url: str = self._extract_required_from_extra(REPOSITORY_URL_KEY, "repository to clone")
        declared_versions: list = self._extract_required_from_extra(VERSIONS_KEY, "versions to build")
        self.versions: list = self._create_versions(declared_versions)

    # -- Public: settings ---------------------------------------------------------------

    @property
    def site_url(self) -> str:
        return self.values["site_url"]

    @property
    def project_path(self) -> str:
        """The project path on its domain, from "homepage" (https://openflexo.org/my_project/ gives "my_project")."""
        homepage_url: str = self.values["extra"].get("homepage", "")
        return urlparse(homepage_url).path.strip("/")

    @property
    def other_websites(self) -> list:
        return self.values["extra"].get(GLOBAL_SEARCH_KEY, [])

    # -- Public: versions ---------------------------------------------------------------

    @property
    def latest_version(self) -> WebsiteVersion:
        return next(version for version in self.versions if version.is_latest)

    @property
    def earlier_versions(self) -> list:
        return [version for version in self.versions if not version.is_latest]

    def site_url_of(self, version: WebsiteVersion) -> str:
        """The latest version is at the root of the website, an earlier one in the folder named after it."""
        site_url: str = self.site_url.rstrip("/") + "/"
        if version.is_latest:
            return site_url
        return f"{site_url}{version.name}/"

    # -- Private: extraction ------------------------------------------------------------

    def _extract_required_from_extra(self, key: str, purpose: str):
        extra: dict = self.values.get("extra") or {}
        if key not in extra:
            raise SystemExit(f"{self.project_settings_file}: no '{key}' under 'extra:' ({purpose})")
        return extra.pop(key)

    def _check_no_global_navigation(self) -> None:
        if NAVIGATION_KEY in self.values:
            raise SystemExit(f"{self.project_settings_file}: '{NAVIGATION_KEY}' would apply to every version; "
                             "put it in 'navigation' of the version it belongs to")

    # -- Private: versions --------------------------------------------------------------

    def _create_versions(self, declared_versions: list) -> list:
        try:
            versions: list = [WebsiteVersion(declaration) for declaration in declared_versions or []]
        except ValueError as error:
            raise SystemExit(f"{self.project_settings_file}: {error}")
        self._check_versions(versions)
        return versions

    def _check_versions(self, versions: list) -> None:
        names: list = [version.name for version in versions]
        if len(set(names)) != len(names):
            raise SystemExit(f"{self.project_settings_file}: version names must be unique")
        latest_versions_count: int = sum(version.is_latest for version in versions)
        if latest_versions_count != 1:
            raise SystemExit(f"{self.project_settings_file}: exactly one version must have 'is_latest: true' "
                             f"(found {latest_versions_count})")

    # -- Private: merge -----------------------------------------------------------------

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


# -- Public: YAML files -----------------------------------------------------------------

def read_yaml(file: Path) -> dict:
    return yaml.safe_load(file.read_text(encoding="utf-8"))


def write_yaml(file: Path, content: dict) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True), encoding="utf-8")
