from pathlib import Path
from urllib.parse import urlparse

import yaml


TOOL_FOLDER: Path = Path(__file__).parent.parent
SHARED_FOLDER: Path = TOOL_FOLDER / "shared"
SHARED_SETTINGS_FILE: Path = SHARED_FOLDER / "site_settings.yml"
SHARED_STYLE_AND_ICON_FOLDER: Path = SHARED_FOLDER / "style_and_icon"
SHARED_HTML_TEMPLATES_FOLDER: Path = SHARED_FOLDER / "html_templates"

SOURCES_KEY: str = "documentation_sources"
GLOBAL_SEARCH_KEY: str = "global_search"


class WebsiteSettings:
    """The settings shared by every website, completed by the settings of one project."""

    def __init__(self, project_settings_file: Path):
        self.project_settings_file: Path = project_settings_file
        self.values: dict = self._merge(read_yaml(SHARED_SETTINGS_FILE), read_yaml(project_settings_file))
        self.sources: list = self._extract_declared_sources()

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
    def previous_versions(self) -> list:
        return self.values["extra"].get("previous_versions", [])

    @property
    def other_websites(self) -> list:
        return self.values["extra"].get(GLOBAL_SEARCH_KEY, [])

    # -- Private: sources ---------------------------------------------------------------

    def _extract_declared_sources(self) -> list:
        extra: dict = self.values.get("extra") or {}
        if SOURCES_KEY not in extra:
            raise SystemExit(f"{self.project_settings_file}: no '{SOURCES_KEY}' list under 'extra:' (folders to copy)")
        return extra.pop(SOURCES_KEY)

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
