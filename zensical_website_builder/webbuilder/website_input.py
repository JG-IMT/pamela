import copy
import json
import os
import shutil
from pathlib import Path

from webbuilder.markdown_links import MarkdownLinks
from webbuilder.website_settings import (
    SHARED_HTML_TEMPLATES_FOLDER, SHARED_STYLE_AND_ICON_FOLDER, WebsiteSettings, write_yaml,
)

INPUT_FOLDER_NAME: str = "input"
OUTPUT_FOLDER_NAME: str = "output"
ZENSICAL_CONFIG_FILE_NAME: str = "zensical_config.yml"
VERSIONS_FILE_NAME: str = "versions.json"


class WebsiteInput:
    """What Zensical builds a website from: the input folder and its config file."""

    def __init__(self, settings: WebsiteSettings, build_folder: Path, displayed_version: str):
        self.settings: WebsiteSettings = settings
        self.displayed_version: str = displayed_version
        self.input_folder: Path = build_folder / INPUT_FOLDER_NAME
        self.zensical_config_file: Path = build_folder / ZENSICAL_CONFIG_FILE_NAME

    # -- Public: entry point ------------------------------------------------------------

    def prepare(self, clean_first: bool) -> Path:
        if clean_first:
            self._delete_input_folder()

        self._copy_folder(SHARED_STYLE_AND_ICON_FOLDER, self.input_folder)
        self._copy_declared_sources()
        relative_links_count: int = MarkdownLinks(self.input_folder).make_relative()
        self._write_versions_file()
        self._write_zensical_config()

        markdown_pages: list = list(self.input_folder.rglob("*.md"))
        print(f"Prepared {len(markdown_pages)} Markdown pages in {self.input_folder} "
              f"({relative_links_count} links made relative)")
        return self.zensical_config_file

    # -- Private: files -----------------------------------------------------------------

    def _delete_input_folder(self) -> None:
        """Not the default: under a running "zensical serve" it loses the stylesheet."""
        if self.input_folder.exists():
            shutil.rmtree(self.input_folder)

    def _copy_declared_sources(self) -> None:
        for source_entry in self.settings.sources:
            source_folder: Path = self.settings.project_settings_file.parent / source_entry["source"]
            self._copy_folder(source_folder, self.input_folder / source_entry["destination"])

    @staticmethod
    def _copy_folder(source_folder: Path, destination_folder: Path) -> None:
        shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)

    # -- Private: versions --------------------------------------------------------------

    def _write_versions_file(self) -> None:
        """Read by the version menu of every page: the current version first, then the earlier ones."""
        current_version: dict = {"name": self.displayed_version, "link": self.settings.site_url, "current": True}
        versions: list = [current_version] + self.settings.previous_versions
        (self.input_folder / VERSIONS_FILE_NAME).write_text(json.dumps(versions, indent=2), encoding="utf-8")

    # -- Private: Zensical config -------------------------------------------------------

    def _write_zensical_config(self) -> None:
        """Paths are relative to the generated config file, which is where Zensical reads them from."""
        zensical_config: dict = copy.deepcopy(self.settings.values)
        templates_path: str = os.path.relpath(SHARED_HTML_TEMPLATES_FOLDER, self.zensical_config_file.parent)
        zensical_config["docs_dir"] = INPUT_FOLDER_NAME
        zensical_config["site_dir"] = OUTPUT_FOLDER_NAME
        zensical_config["theme"]["custom_dir"] = Path(templates_path).as_posix()
        zensical_config["extra"]["displayed_version"] = self.displayed_version
        write_yaml(self.zensical_config_file, zensical_config)
