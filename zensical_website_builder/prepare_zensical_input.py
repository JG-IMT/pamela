"""
Prepares the single folder Zensical builds the website from (the config's docs_dir), out of
the Markdown and images a repository keeps in several places.

Which folders to copy is read from the project's own config, under "extra.documentation_sources".
Usage:
    python prepare_zensical_input.py <path to mkdocs.yml> [--clean]
"""
import argparse
import shutil
from pathlib import Path

import yaml


SOURCES_KEY: str = "documentation_sources"


class _ConfigLoader(yaml.SafeLoader):
    """Skips the tags only Zensical understands (!ENV...): this script reads plain keys."""


_ConfigLoader.add_multi_constructor("", lambda loader, tag, node: None)


# -- Public: entry point ----------------------------------------------------------------

def prepare_zensical_input(config_file: Path, clean_first: bool) -> None:
    config: dict = _read_config(config_file)
    input_folder: Path = config_file.parent / config["docs_dir"]
    source_entries: list = _read_declared_sources(config, config_file)

    # --clean: a page deleted from the repository can no longer linger
    if clean_first:
        _delete_folder(input_folder)

    _copy_declared_sources(config_file.parent, source_entries, input_folder)
    print(f"Prepared {_count_markdown_pages(input_folder)} Markdown pages in {input_folder}")


# -- Private: preparation steps ---------------------------------------------------------

def _read_config(config_file: Path) -> dict:
    return yaml.load(config_file.read_text(encoding="utf-8"), Loader=_ConfigLoader)


def _read_declared_sources(config: dict, config_file: Path) -> list:
    if SOURCES_KEY not in (config.get("extra") or {}):
        raise SystemExit(f"{config_file}: no '{SOURCES_KEY}' list under 'extra:' (folders to copy)")
    return config["extra"][SOURCES_KEY]


def _delete_folder(folder: Path) -> None:
    """Not the default: under a running "zensical serve" it loses the stylesheet."""
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
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Prepares the folder Zensical builds the website from."
    )
    parser.add_argument("config_file", type=Path, help="Zensical config of the project")
    parser.add_argument("--clean", action="store_true", help="delete the input folder first")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    prepare_zensical_input(arguments.config_file, arguments.clean)
