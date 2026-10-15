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
    """The Markdown pages of the input folder, whose links starting with "/" are fixed.

    A link starting with "/" leads to the root of the domain, not to the root of the website.
    For each link, in the copies of the pages (never in the sources):
      1. the target is in the website: the link becomes relative to the page
      2. the link already starts with the project path (/my_project/javadoc/...): unchanged
      3. otherwise the project path is put in front (/javadoc/... becomes /my_project/javadoc/...)
    """

    def __init__(self, input_folder: Path, project_path: str = ""):
        self.input_folder: Path = input_folder
        self.project_path: str = project_path

    # -- Public: entry point ------------------------------------------------------------

    def fix(self) -> None:
        for page in self.input_folder.rglob("*.md"):
            self._fix_page(page)

    # -- Private: pages -----------------------------------------------------------------

    def _fix_page(self, page: Path) -> None:
        page_folder: str = page.parent.relative_to(self.input_folder).as_posix()
        text: str = page.read_text(encoding="utf-8")
        lines: list = text.split("\n")
        inside_code_block: bool = False

        def fixed_link(link: re.Match) -> str:
            return link["start"] + self._fixed_address(link["path"], page_folder)

        for line_index, line in enumerate(lines):
            if CODE_BLOCK_MARKER.match(line):
                inside_code_block = not inside_code_block
            elif not inside_code_block:
                lines[line_index] = LINK_STARTING_WITH_SLASH.sub(fixed_link, line)

        fixed_text: str = "\n".join(lines)
        if fixed_text != text:
            page.write_text(fixed_text, encoding="utf-8")

    # -- Private: links -----------------------------------------------------------------

    def _fixed_address(self, path: str, page_folder: str) -> str:
        """The address (path without its first "/") as it must be written in the page."""
        target: str = re.split(r"[#?]", path)[0]
        if (self.input_folder / target).exists():
            return posixpath.relpath(path, start=page_folder)
        if not self.project_path or path.startswith(self.project_path + "/"):
            return "/" + path
        return f"/{self.project_path}/{path}"
