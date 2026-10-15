import posixpath
import re
from pathlib import Path

# A link whose address starts with a single "/": ![](/images/a.png), src="/images/a.png", href="/files/a.zip"
#   start: what comes before the address ("](", src=" or href=")
#   path:  the address without its first "/" (up to ")", a quote or a space)
#   not matched: an external address starting with two slashes, like //cdn.example.org/a.png
LINK_STARTING_WITH_SLASH: re.Pattern = re.compile(r'(?P<start>\]\(|\b(?:src|href)=")/(?!/)(?P<path>[^)"\s]+)')
CODE_BLOCK_MARKER: re.Pattern = re.compile(r"^\s*(```|~~~)")


class MarkdownLinks:
    """The Markdown pages of the input folder, whose links starting with "/" are made relative.

    A link starting with "/" leads to the root of the domain, not to the root of the website, so it
    breaks once the website is published under a sub-path (e.g. openflexo.org/<project>/docs/).
    Only the copies in the input folder are changed, never the sources.
    """

    def __init__(self, input_folder: Path):
        self.input_folder: Path = input_folder

    # -- Public: entry point ------------------------------------------------------------

    def make_relative(self) -> int:
        """Returns the number of links converted."""
        converted_links_count: int = 0
        for page in self.input_folder.rglob("*.md"):
            converted_links_count += self._make_page_relative(page)
        return converted_links_count

    # -- Private: pages -----------------------------------------------------------------

    def _make_page_relative(self, page: Path) -> int:
        page_folder: str = page.parent.relative_to(self.input_folder).as_posix()
        lines: list = page.read_text(encoding="utf-8").split("\n")
        converted_links_count: int = 0
        inside_code_block: bool = False

        def relative_link(link: re.Match) -> str:
            return link["start"] + posixpath.relpath(link["path"], start=page_folder)

        for line_index, line in enumerate(lines):
            if CODE_BLOCK_MARKER.match(line):
                inside_code_block = not inside_code_block
            elif not inside_code_block:
                links_in_line: list = LINK_STARTING_WITH_SLASH.findall(line)
                converted_links_count += len(links_in_line)
                lines[line_index] = LINK_STARTING_WITH_SLASH.sub(relative_link, line)

        if converted_links_count:
            page.write_text("\n".join(lines), encoding="utf-8")
        return converted_links_count
