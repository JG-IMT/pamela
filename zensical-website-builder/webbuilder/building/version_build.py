"""
Builds one version of the website: clones it at its git reference, prepares the input folder
Zensical reads, and runs Zensical on it. The clone is deleted once the version is built, or has
failed; the Zensical input and the version site stay, to see what Zensical was given and what it produced.
"""

import subprocess
import sys
from pathlib import Path

from webbuilder.helper.folder_helper import FolderHelper
from webbuilder.preparation.zensical_input import VERSION_SITE_FOLDER_NAME, ZensicalInput
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings
from webbuilder.settings.website_version import WebsiteVersion

VERSION_CLONE_FOLDER_NAME: str = "version_clone"


class VersionBuild:
    """Builds one version of the website from a clone of its git reference."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(
        self,
        website_settings: WebsiteSettings,
        git_repository: GitRepository,
        version: WebsiteVersion,
        version_build_folder: Path,
    ) -> None:
        self._website_settings: WebsiteSettings = website_settings
        self._git_repository: GitRepository = git_repository
        self._version: WebsiteVersion = version
        self._version_build_folder: Path = version_build_folder

        self._version_clone_folder: Path = version_build_folder.joinpath(VERSION_CLONE_FOLDER_NAME)
        self._version_site_folder: Path = version_build_folder.joinpath(VERSION_SITE_FOLDER_NAME)


    # -- Public: entry point -------------------------------------------------------------------------

    def build(self) -> Path:
        """
        Clones the version, prepares its input folder, runs Zensical, then deletes the clone - also
        when the build fails. Returns the version site folder, which holds the pages of the version.
        """
        print(f"Building version {self._version.get_name()} ({self._version.get_git_ref()})")
        self._clone_version()
        try:
            zensical_input: ZensicalInput = self._create_zensical_input()
            zensical_input.prepare_input()
            self._run_zensical(zensical_input.write_config())
        finally:
            FolderHelper.delete_folder(self._version_clone_folder)
        return self._version_site_folder


    # -- Private: build steps ------------------------------------------------------------------------

    def _clone_version(self) -> None:
        """Clones the git reference of the version into the clone folder."""
        self._git_repository.clone_at(self._version.get_git_ref(), self._version_clone_folder)


    def _create_zensical_input(self) -> ZensicalInput:
        """The input of Zensical for the version, to write from the clone of the version."""
        return ZensicalInput(
            self._website_settings, self._version_clone_folder, self._version_build_folder, self._version
        )


    def _run_zensical(self, zensical_config_file: Path) -> None:
        """Runs the Zensical installed for the Python running the website builder. Stops the build if it fails."""
        zensical_result: subprocess.CompletedProcess = subprocess.run(
            [sys.executable, "-m", "zensical", "build", "--clean", "-f", str(zensical_config_file)]
        )
        if zensical_result.returncode != 0:
            raise SystemExit(f"Zensical failed on version {self._version.get_name()}")
