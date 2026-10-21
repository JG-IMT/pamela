"""
Builds every version of the website and assembles them in one website folder: the latest version
at its root, each earlier version in a folder named after it. The assembly is made in a folder of
its own and only replaces the previous website once every version is built, so a failed build never
leaves a website with missing versions.
"""

from pathlib import Path

from webbuilder.building.version_build import VersionBuild
from webbuilder.helper.folder_helper import FolderHelper
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings
from webbuilder.settings.website_version import WebsiteVersion

VERSION_BUILDS_FOLDER_NAME: str = "version_builds"
WEBSITE_FOLDER_NAME: str = "website"
WEBSITE_IN_PROGRESS_FOLDER_NAME: str = "website_in_progress"


class WebsiteBuild:
    """Builds every version of the website and assembles them in a single website folder."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, website_settings: WebsiteSettings, git_repository: GitRepository, build_folder: Path) -> None:
        self._website_settings: WebsiteSettings = website_settings
        self._git_repository: GitRepository = git_repository

        self._version_builds_folder: Path = build_folder.joinpath(VERSION_BUILDS_FOLDER_NAME)  # one work folder per version
        self._website_in_progress_folder: Path = build_folder.joinpath(WEBSITE_IN_PROGRESS_FOLDER_NAME)
        self._website_folder: Path = build_folder.joinpath(WEBSITE_FOLDER_NAME)


    # -- Public: entry point -------------------------------------------------------------------------

    def build(self) -> Path:
        """
        Builds each declared version into the website in progress, then replaces the previous website
        by it. Stops at the first version that fails, keeping the previous website.
        Returns the website folder.
        """
        self._delete_previous_build()
        
        for version in self._website_settings.get_version_catalog().get_all_versions():
            version_site_folder: Path = self._build_version(version)
            self._add_version_to_website(version, version_site_folder)
        self._replace_website()

        print(f"Website built in {self._website_folder}")
        return self._website_folder


    # -- Private: build steps ------------------------------------------------------------------------

    def _delete_previous_build(self) -> None:
        FolderHelper.delete_folder(self._version_builds_folder)
        FolderHelper.delete_folder(self._website_in_progress_folder)


    def _build_version(self, version: WebsiteVersion) -> Path:
        """Builds the version in its own work folder. Returns the folder of the site of the version."""
        version_build_folder: Path = self._version_builds_folder.joinpath(version.get_name())
        
        version_build: VersionBuild = VersionBuild(self._website_settings, self._git_repository, version, version_build_folder)
        return version_build.build()


    def _add_version_to_website(self, version: WebsiteVersion, version_site_folder: Path) -> None:
        """Copies the site of the version into the website in progress: at the root for the latest, else in its folder."""
        folder_of_version: str = self._website_settings.get_version_catalog().folder_of(version)
        FolderHelper.copy_folder(version_site_folder, self._website_in_progress_folder.joinpath(folder_of_version))


    def _replace_website(self) -> None:
        """Puts the website in progress in place of the previous website, deleted only now that every version is built."""
        FolderHelper.delete_folder(self._website_folder)
        self._website_in_progress_folder.rename(self._website_folder)
