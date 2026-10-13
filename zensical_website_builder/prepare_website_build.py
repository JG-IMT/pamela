"""
Prepares what Zensical needs to build a website:
  - the input folder: the project's Markdown and images, plus the files shared by every website
  - the config file: the shared settings completed by the project's own settings

Usage:
    python prepare_website_build.py --settings <website_settings.yml> --build-folder <folder>
                                    [--version 1.2.3] [--clean]
Then build with:  zensical build -f <folder>/zensical_config.yml
"""
import argparse
import os
import shutil
from pathlib import Path

import yaml


TOOL_FOLDER: Path = Path(__file__).parent
SHARED_SETTINGS_FILE: Path = TOOL_FOLDER / "shared_site_settings.yml"
SHARED_STYLE_AND_ICON_FOLDER: Path = TOOL_FOLDER / "shared_style_and_icon"
SHARED_HTML_TEMPLATES_FOLDER: Path = TOOL_FOLDER / "shared_html_templates"

INPUT_FOLDER_NAME: str = "input"
OUTPUT_FOLDER_NAME: str = "output"
ZENSICAL_CONFIG_FILE_NAME: str = "zensical_config.yml"

SOURCES_KEY: str = "documentation_sources"
DEFAULT_VERSION: str = "dev"


# -- Public: entry point ----------------------------------------------------------------

def prepare_website_build(settings_file: Path, build_folder: Path, displayed_version: str,
                          clean_first: bool) -> Path:
    input_folder: Path = build_folder / INPUT_FOLDER_NAME
    settings: dict = _merge_settings(_read_yaml(SHARED_SETTINGS_FILE), _read_yaml(settings_file))
    source_entries: list = _extract_declared_sources(settings, settings_file)

    if clean_first:
        _delete_folder(input_folder)

    _copy_folder(SHARED_STYLE_AND_ICON_FOLDER, input_folder)
    _copy_declared_sources(settings_file.parent, source_entries, input_folder)

    zensical_config_file: Path = build_folder / ZENSICAL_CONFIG_FILE_NAME
    _complete_settings_for_zensical(settings, zensical_config_file, displayed_version)
    _write_yaml(zensical_config_file, settings)

    print(f"Prepared {_count_markdown_pages(input_folder)} Markdown pages in {input_folder}")
    return zensical_config_file


# -- Private: settings ------------------------------------------------------------------

def _merge_settings(shared: dict, project: dict) -> dict:
    """The project wins; nested sections are merged key by key, lists are replaced."""
    merged: dict = dict(shared)
    for key, project_value in project.items():
        shared_value = shared.get(key)
        if isinstance(shared_value, dict) and isinstance(project_value, dict):
            merged[key] = _merge_settings(shared_value, project_value)
        else:
            merged[key] = project_value
    return merged


def _extract_declared_sources(settings: dict, settings_file: Path) -> list:
    extra: dict = settings.get("extra") or {}
    if SOURCES_KEY not in extra:
        raise SystemExit(f"{settings_file}: no '{SOURCES_KEY}' list under 'extra:' (folders to copy)")
    return extra.pop(SOURCES_KEY)


def _complete_settings_for_zensical(settings: dict, zensical_config_file: Path,
                                    displayed_version: str) -> None:
    """Paths are relative to the generated config file, which is where Zensical reads them from."""
    templates_path: str = os.path.relpath(SHARED_HTML_TEMPLATES_FOLDER, zensical_config_file.parent)
    settings["docs_dir"] = INPUT_FOLDER_NAME
    settings["site_dir"] = OUTPUT_FOLDER_NAME
    settings["theme"]["custom_dir"] = Path(templates_path).as_posix()
    settings["extra"]["displayed_version"] = displayed_version


def _read_yaml(file: Path) -> dict:
    return yaml.safe_load(file.read_text(encoding="utf-8"))


def _write_yaml(file: Path, content: dict) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True), encoding="utf-8")


# -- Private: files ---------------------------------------------------------------------

def _copy_declared_sources(settings_folder: Path, source_entries: list, input_folder: Path) -> None:
    for source_entry in source_entries:
        source_folder: Path = settings_folder / source_entry["source"]
        destination_folder: Path = input_folder / source_entry["destination"]
        _copy_folder(source_folder, destination_folder)


def _copy_folder(source_folder: Path, destination_folder: Path) -> None:
    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)


def _delete_folder(folder: Path) -> None:
    """Not the default: under a running "zensical serve" it loses the stylesheet."""
    if folder.exists():
        shutil.rmtree(folder)


def _count_markdown_pages(input_folder: Path) -> int:
    return sum(1 for _ in input_folder.rglob("*.md"))


# -- Private: command line --------------------------------------------------------------

def _parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Prepares the input folder and the config Zensical builds a website from."
    )
    parser.add_argument("--settings", type=Path, required=True, help="website_settings.yml of the project")
    parser.add_argument("--build-folder", type=Path, required=True, help="folder receiving everything generated")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="version shown in the website")
    parser.add_argument("--clean", action="store_true", help="delete the input folder first")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    generated_config: Path = prepare_website_build(
        arguments.settings, arguments.build_folder, arguments.version, arguments.clean
    )
    print(f"Zensical config: {generated_config}")
