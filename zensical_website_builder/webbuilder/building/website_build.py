"""
Builds every version of the website and assembles them in one output folder: the latest version
at its root, each earlier version in a folder named after it. The assembly is made in a folder of
its own and only replaces the previous output once every version is built, so a failed build never
leaves a website with missing versions.
"""

import shutil
from pathlib import Path

from webbuilder.building.version_build import VersionBuild
from webbuilder.preparation.version_site_input import OUTPUT_FOLDER_NAME
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings

VERSION_BUILDS_FOLDER_NAME: str = "versions"
OUTPUT_IN_PROGRESS_FOLDER_NAME: str = "output_in_progress"


class WebsiteBuild:
    """Builds every version of the website and assembles them in a single output folder."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, settings: WebsiteSettings, git_repository: GitRepository, build_folder: Path) -> None:
        self.settings: WebsiteSettings = settings
        self.git_repository: GitRepository = git_repository

        self.version_builds_folder: Path = build_folder / VERSION_BUILDS_FOLDER_NAME  # one build folder per version
        self.output_in_progress_folder: Path = build_folder / OUTPUT_IN_PROGRESS_FOLDER_NAME
        self.output_folder: Path = build_folder / OUTPUT_FOLDER_NAME


    # -- Public: entry point -------------------------------------------------------------------------

    def build(self) -> Path:
        """
        Builds each declared version, copies it into the output in progress, then replaces the
        previous output by it. Stops at the first version that fails, keeping the previous output.
        Returns the output folder.
        """
        GitRepository.delete_folder_with_clones(self.version_builds_folder)  # may hold the clones of an older build
        self._delete_folder(self.output_in_progress_folder)

        for version in self.settings.versions:
            version_build: VersionBuild = VersionBuild(
                self.settings, self.git_repository, version, self.version_builds_folder / version.name
            )
            version_folder: Path = self.output_in_progress_folder / self.settings.versions.folder_of(version)
            shutil.copytree(version_build.build(), version_folder, dirs_exist_ok=True)

        self._delete_folder(self.output_folder)
        self.output_in_progress_folder.rename(self.output_folder)

        print(f"Website built in {self.output_folder}")
        return self.output_folder


    # -- Private: folders ----------------------------------------------------------------------------

    @staticmethod
    def _delete_folder(folder: Path) -> None:
        if folder.exists():
            shutil.rmtree(folder)
