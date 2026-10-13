"""
Prepares the single folder Zensical builds the website from (the config's docs_dir), out of
the Markdown and images a repository keeps in several places.

Which folders to copy is read from the project's own config, under "documentation_sources". 
Usage:
    python prepare_zensical_input.py <path to mkdocs.yml> [--clean]
"""
import argparse
import shutil
from pathlib import Path

import yaml


SOURCES_KEY: str = "documentation_sources"


class _ConfigLoader(yaml.SafeLoader):
    """
    Zensical configs can contain tags only Zensical understands (!ENV, !!python/name:...).
    This script reads plain keys only, so those tags are skipped instead of making it fail.
    """


_ConfigLoader.add_multi_constructor("", lambda loader, tag, node: None)


# -- Public: entry point ----------------------------------------------------------------

def prepare_zensical_input(config_file: Path, clean_first: bool) -> None:
    config: dict = _read_config(config_file)
    input_folder: Path = config_file.parent / config["docs_dir"]

    # clean_first is True when --clean is passed: a page deleted from the repository
    # can then no longer linger in the website
    if clean_first:
        _delete_folder(input_folder)

    _copy_declared_sources(config_file.parent, config[SOURCES_KEY], input_folder)
    print(f"Prepared {_count_markdown_pages(input_folder)} Markdown pages in {input_folder}")


# -- Private: preparation steps ---------------------------------------------------------

def _read_config(config_file: Path) -> dict:
    return yaml.load(config_file.read_text(encoding="utf-8"), Loader=_ConfigLoader)


def _delete_folder(folder: Path) -> None:
    """
    Not done by default: deleting the folder under a running "zensical serve" makes it
    drop the stylesheet from the website until it is restarted.
    """
    if folder.exists():
        shutil.rmtree(folder)


def _copy_declared_sources(config_folder: Path, source_entries: list, input_folder: Path) -> None:
    for source_entry in source_entries:
        source_folder: Path = config_folder / source_entry["source"]
        destination_folder: Path = input_folder / source_entry["destination"]
        _copy_folder(source_folder, destination_folder)


def _copy_folder(source_folder: Path, destination_folder: Path) -> None:
    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)


def _count_markdown_pages(input_folder: Path) -> int:
    return sum(1 for _ in input_folder.rglob("*.md"))


def _parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("config_file", type=Path, help="Zensical config of the project (mkdocs.yml)")
    parser.add_argument("--clean", action="store_true", help="delete the input folder first")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    prepare_zensical_input(arguments.config_file, arguments.clean)
