"""
Entry point of the website builder.

Usage:
    python main.py prepare --settings <website_settings.yml> --build-folder <folder>
                           [--version 1.2.3] [--clean]
        Prepares what Zensical needs: the input folder (the project's Markdown and images, plus the
        files shared by every website) and the config file. Then build with:
        zensical build -f <folder>/zensical_config.yml

    python main.py search --settings <website_settings.yml> --build-folder <folder>
        After the build, adds the pages of the websites declared under extra.global_search
        (website_settings.yml) to the search index of the built website:
            extra:
              global_search:
                - name: Connie
                  site_url: https://openflexo.org/connie/docs/
"""
import argparse
from pathlib import Path

from webbuilder.search_index import SEARCH_INDEX_FILE_NAME, SearchIndex
from webbuilder.website_input import OUTPUT_FOLDER_NAME, WebsiteInput
from webbuilder.website_settings import WebsiteSettings

DEFAULT_VERSION: str = "dev"


# -- Commands ---------------------------------------------------------------------------

def _prepare(arguments: argparse.Namespace) -> None:
    website_input: WebsiteInput = WebsiteInput(
        WebsiteSettings(arguments.settings), arguments.build_folder, arguments.version
    )
    print(f"Zensical config: {website_input.prepare(arguments.clean)}")


def _search(arguments: argparse.Namespace) -> None:
    settings: WebsiteSettings = WebsiteSettings(arguments.settings)
    search_index: SearchIndex = SearchIndex(
        arguments.build_folder / OUTPUT_FOLDER_NAME / SEARCH_INDEX_FILE_NAME, settings.site_url
    )
    added_entries_count: int = search_index.add_other_websites(settings.other_websites)
    search_index.save()
    print(f"Added {added_entries_count} search entries from {len(settings.other_websites)} other website(s)")


# -- Command line -----------------------------------------------------------------------

def _parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Website builder, based on Zensical.")
    commands = parser.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare", help="prepare the input folder and the config of Zensical")
    prepare_parser.add_argument("--version", default=DEFAULT_VERSION, help="version shown in the website")
    prepare_parser.add_argument("--clean", action="store_true", help="delete the input folder first")
    prepare_parser.set_defaults(run=_prepare)

    search_parser = commands.add_parser("search", help="add the pages of other websites to the search index")
    search_parser.set_defaults(run=_search)

    for command_parser in (prepare_parser, search_parser):
        command_parser.add_argument("--settings", type=Path, required=True, help="website_settings.yml of the project")
        command_parser.add_argument("--build-folder", type=Path, required=True, help="folder holding everything generated")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    arguments.run(arguments)
