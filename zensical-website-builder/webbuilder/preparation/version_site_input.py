"""
Prepares what Zensical needs to build one version of the website: the input folder (the shared
style and icon, the Markdown pages and images of the version, the menu of versions) and the
Zensical config file. The folder holding the sources of the version (its clone) is given.
"""

import copy
import json
import os
import posixpath
import shutil
from pathlib import Path

import yaml

from webbuilder.preparation.markdown_path_rewriter import MarkdownPathRewriter
from webbuilder.preparation.website_path_resolver import WebsitePathResolver
from webbuilder.settings.website_settings import WebsiteSettings
from webbuilder.settings.website_versions import WebsiteVersion, WebsiteVersions
from webbuilder.shared_files import SHARED_HTML_TEMPLATES_FOLDER, SHARED_STYLE_AND_ICON_FOLDER

MARKDOWN_EXTENSION: str = ".md"
ZENSICAL_INPUT_FOLDER_NAME: str = "zensical_input"
VERSION_SITE_FOLDER_NAME: str = "version_site"
ZENSICAL_CONFIG_FILE_NAME: str = "zensical_config.yml"
VERSIONS_FILE_NAME: str = "versions.json"


class VersionSiteInput:
    """Prepares the input folder and the Zensical config file from which the site of one version is built."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(
        self,
        settings: WebsiteSettings,
        repository_folder: Path,
        build_folder: Path,
        version: WebsiteVersion,
    ) -> None:
        self.settings: WebsiteSettings = settings
        self.repository_folder: Path = repository_folder  # the clone of the version: its sources
        self.version: WebsiteVersion = version

        self.zensical_input_folder: Path = build_folder / ZENSICAL_INPUT_FOLDER_NAME
        self.zensical_config_file: Path = build_folder / ZENSICAL_CONFIG_FILE_NAME


    # -- Public: entry point -------------------------------------------------------------------------

    def prepare(self) -> Path:
        """
        Starts from an empty input folder, copies the shared style and the declared sources into it,
        rewrites the paths starting with "/" in the copies of the pages, then writes the menu of
        versions and the Zensical config. Stops, naming the version, if a source folder is missing or
        if no Markdown page is found. Returns the Zensical config file.
        """
        self._delete_zensical_input_folder()

        self._copy_folder(SHARED_STYLE_AND_ICON_FOLDER, self.zensical_input_folder)
        self._copy_declared_sources()

        markdown_page_files: list[Path] = self._markdown_page_files()
        if not markdown_page_files:
            raise SystemExit(f"Version {self.version.name}: no Markdown page in the declared sources")
        self._rewrite_paths_in(markdown_page_files)

        self._write_versions_file()
        self._write_zensical_config()

        print(f"Prepared {len(markdown_page_files)} Markdown pages in {self.zensical_input_folder}")
        return self.zensical_config_file


    # -- Private: files ------------------------------------------------------------------------------

    def _delete_zensical_input_folder(self) -> None:
        if self.zensical_input_folder.exists():
            shutil.rmtree(self.zensical_input_folder)


    def _copy_declared_sources(self) -> None:
        for source_entry in self.settings.sources:
            source_folder: Path = self.repository_folder / source_entry["source"]
            if not source_folder.is_dir():
                raise SystemExit(f"Version {self.version.name}: folder '{source_entry['source']}' not found")
            self._copy_folder(source_folder, self.zensical_input_folder / source_entry["destination"])


    @staticmethod
    def _copy_folder(source_folder: Path, destination_folder: Path) -> None:
        shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)


    def _markdown_page_files(self) -> list[Path]:
        markdown_page_files: list[Path] = []
        for walked_folder, subfolder_names, file_names in os.walk(self.zensical_input_folder):
            for file_name in file_names:
                if file_name.endswith(MARKDOWN_EXTENSION):
                    markdown_page_files.append(Path(walked_folder) / file_name)
        return markdown_page_files


    # -- Private: pages ------------------------------------------------------------------------------

    def _rewrite_paths_in(self, markdown_page_files: list[Path]) -> None:
        path_resolver: WebsitePathResolver = WebsitePathResolver(
            self.zensical_input_folder, self.settings.project_url_path
        )
        MarkdownPathRewriter(path_resolver).rewrite_paths_in(markdown_page_files)


    # -- Private: menu of versions -------------------------------------------------------------------

    def _write_versions_file(self) -> None:
        """Read by the version menu of every page: the latest version first, then the earlier ones."""
        versions: list[WebsiteVersion] = [self.settings.versions.latest] + self.settings.versions.earlier
        menu_entries: list[dict] = [
            {"name": version.name, "link": self._path_to_root_of(version), "current": version.name == self.version.name}
            for version in versions
        ]
        versions_file: Path = self.zensical_input_folder / VERSIONS_FILE_NAME
        versions_file.write_text(json.dumps(menu_entries, indent=2), encoding="utf-8")


    def _path_to_root_of(self, target_version: WebsiteVersion) -> str:
        """From the root of this version: "." for itself, "../1.6" for the folder of another version."""
        versions: WebsiteVersions = self.settings.versions
        return posixpath.relpath(versions.folder_of(target_version), start=versions.folder_of(self.version))


    # -- Private: Zensical config --------------------------------------------------------------------

    def _write_zensical_config(self) -> None:
        # Paths are relative to the generated config file, which is where Zensical reads them from.
        zensical_config: dict = copy.deepcopy(self.settings.zensical_values)
        templates_path: str = os.path.relpath(SHARED_HTML_TEMPLATES_FOLDER, self.zensical_config_file.parent)
        latest_version: WebsiteVersion = self.settings.versions.latest

        zensical_config["site_url"] = self.settings.versions.site_url_of(self.version)
        zensical_config["docs_dir"] = ZENSICAL_INPUT_FOLDER_NAME
        zensical_config["site_dir"] = VERSION_SITE_FOLDER_NAME
        zensical_config["theme"]["custom_dir"] = Path(templates_path).as_posix()

        # Read by the page templates (shared/html_templates): the version badge, and the banner of an
        # earlier version linking to the latest one.
        zensical_config["extra"]["displayed_version"] = self.version.name
        zensical_config["extra"]["latest_version"] = latest_version.name
        zensical_config["extra"]["latest_version_url"] = self.settings.versions.site_url_of(latest_version)

        if self.version.navigation:
            zensical_config["nav"] = self.version.navigation

        self._write_yaml_file(self.zensical_config_file, zensical_config)


    @staticmethod
    def _write_yaml_file(file: Path, content: dict) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True), encoding="utf-8")
