"""
Entry point of the website builder.

Usage:
    python main.py --settings <website_settings.yml>
        Clones each version declared in website_settings.yml at its git_ref, builds it with Zensical and
        assembles the website in <build folder>/website: the latest version at its root, each earlier
        version in a folder named after it. The "build" folder is created next to website_settings.yml.
"""

import argparse
from pathlib import Path

from webbuilder.building.website_build import WebsiteBuild
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings

BUILD_FOLDER_NAME: str = "build"


# -- Build ----------------------------------------------------------------------------------------------

def _build_website(project_settings_file: Path) -> None:
    website_settings: WebsiteSettings = WebsiteSettings(project_settings_file)
    git_repository: GitRepository = GitRepository(website_settings.get_repository_url())
    WebsiteBuild(website_settings, git_repository, project_settings_file.parent.joinpath(BUILD_FOLDER_NAME)).build()


# -- Command line ---------------------------------------------------------------------------------------

def _existing_file(argument: str) -> Path:
    file: Path = Path(argument)
    if not file.is_file():
        raise argparse.ArgumentTypeError(f"{file} is not an existing file (expected a website_settings.yml)")
    return file


def _parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Builds the website, with all its versions, from the Markdown of a repository, using Zensical."
    )
    # python main.py --settings website_settings.yml
    parser.add_argument("--settings", type=_existing_file, required=True, help="website_settings.yml of the project")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    _build_website(arguments.settings)
