"""
Builds one version of the website: clones it at its git reference, prepares the input folder
Zensical reads, and runs Zensical on it. The clone is deleted once the version is built, or has
failed; the input and output folders stay, to see what Zensical was given and what it produced.
"""

import subprocess
import sys
from pathlib import Path

from webbuilder.preparation.version_site_input import OUTPUT_FOLDER_NAME, VersionSiteInput
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings
from webbuilder.settings.website_versions import WebsiteVersion

REPOSITORY_FOLDER_NAME: str = "repository"


class VersionBuild:
    """Builds one version of the website from a clone of its git reference."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(
        self,
        settings: WebsiteSettings,
        git_repository: GitRepository,
        version: WebsiteVersion,
        version_build_folder: Path,
    ) -> None:
        self.settings: WebsiteSettings = settings
        self.git_repository: GitRepository = git_repository
        self.version: WebsiteVersion = version
        self.version_build_folder: Path = version_build_folder

        self.repository_folder: Path = version_build_folder / REPOSITORY_FOLDER_NAME  # the clone of the version
        self.output_folder: Path = version_build_folder / OUTPUT_FOLDER_NAME


    # -- Public: entry point -------------------------------------------------------------------------

    def build(self) -> Path:
        """
        Clones the version, prepares its input folder, runs Zensical, then deletes the clone - also
        when the build fails. Returns the output folder, which holds the pages of the version.
        """
        print(f"Building version {self.version.name} ({self.version.git_ref})")
        self.git_repository.clone_at(self.version.git_ref, self.repository_folder)
        try:
            version_site_input: VersionSiteInput = VersionSiteInput(
                self.settings, self.repository_folder, self.version_build_folder, self.version
            )
            self._run_zensical(version_site_input.prepare(clean_first=True))
        finally:
            GitRepository.delete_folder_with_clones(self.repository_folder)
        return self.output_folder


    # -- Private: Zensical ---------------------------------------------------------------------------

    def _run_zensical(self, zensical_config_file: Path) -> None:
        """Zensical is the one installed for the Python running this tool."""
        result: subprocess.CompletedProcess = subprocess.run(
            [sys.executable, "-m", "zensical", "build", "--clean", "-f", str(zensical_config_file)]
        )
        if result.returncode != 0:
            raise SystemExit(f"Zensical failed on version {self.version.name}")
