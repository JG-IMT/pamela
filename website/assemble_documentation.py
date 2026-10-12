"""
Builds the single folder Zensical reads (website/build/documentation/) out of the Markdown
and images this repository keeps in several places.
"""

import shutil
import sys
from pathlib import Path


WEBSITE_FOLDER: Path = Path(__file__).parent
REPOSITORY_ROOT: Path = WEBSITE_FOLDER.parent
ASSEMBLED_DOCUMENTATION: Path = WEBSITE_FOLDER / "build" / "documentation"
BRAND_FOLDER: Path = WEBSITE_FOLDER / "brand"

SOURCE_TO_DESTINATION: dict[Path, Path] = {
    REPOSITORY_ROOT / "src/site/markdown":
        ASSEMBLED_DOCUMENTATION,
    REPOSITORY_ROOT / "pamela-core/src/site/markdown":
        ASSEMBLED_DOCUMENTATION / "pamela-core",
    REPOSITORY_ROOT / "pamela-security-patterns/src/site/markdown":
        ASSEMBLED_DOCUMENTATION / "pamela-security-patterns",
    REPOSITORY_ROOT / "src/site/resources/images":
        ASSEMBLED_DOCUMENTATION / "images",
    REPOSITORY_ROOT / "src/site/resources/img":
        ASSEMBLED_DOCUMENTATION / "img",
    REPOSITORY_ROOT / "src/site/resources/examples":
        ASSEMBLED_DOCUMENTATION / "examples",
    BRAND_FOLDER:
        ASSEMBLED_DOCUMENTATION,
}


# -- Public: entry point ----------------------------------------------------------------

def assemble_documentation(clean_first: bool) -> None:
    
    # clean first is True when using the parameter --clean
    if clean_first:
        _remove_previous_assembly()
        
    for source_folder, destination_folder in SOURCE_TO_DESTINATION.items():
        _copy_folder(source_folder, destination_folder)
        
    print(f"Assembled {_count_pages()} pages into {ASSEMBLED_DOCUMENTATION}")


# -- Private: assembly steps ------------------------------------------------------------

def _remove_previous_assembly() -> None:
    """
    Not the default because deleting the folder under a running "zensical serve" makes it
    drop the stylesheet from the site until it is restarted.
    """
    if ASSEMBLED_DOCUMENTATION.exists():
        shutil.rmtree(ASSEMBLED_DOCUMENTATION)


def _copy_folder(source_folder: Path, destination_folder: Path) -> None:
    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)


def _count_pages() -> int:
    return sum(1 for _ in ASSEMBLED_DOCUMENTATION.rglob("*.md"))


if __name__ == "__main__":
    assemble_documentation(clean_first="--clean" in sys.argv)
