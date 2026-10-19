"""
Rewrites, in the copies of the Markdown pages, the paths that start with "/": finds each path, leaves
the fenced code blocks alone, asks a WebsitePathResolver where the path must point, and writes the
page back only when a path changed. Line endings and the BOM are kept. The sources are never changed,
only the copies it is given.
"""

import re
from pathlib import Path

from webbuilder.preparation.website_path_resolver import WebsitePathResolver

PATH_STARTING_WITH_SLASH: re.Pattern = re.compile(r"""
    (?P<opening> \]\( | \b(?:src|href)=" )
    /(?!/)
    (?P<link_path_without_first_slash> [^)"\s]+ )
""", re.VERBOSE)
CODE_BLOCK_MARKER: re.Pattern = re.compile(r"^\s*(```|~~~)")


class MarkdownPathRewriter:
    """Rewrites the paths starting with "/" in Markdown page files, as decided by a WebsitePathResolver."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, path_resolver: WebsitePathResolver) -> None:
        self.path_resolver: WebsitePathResolver = path_resolver


    # -- Public: entry point -------------------------------------------------------------------------

    def rewrite_paths_in(self, page_files: list[Path]) -> None:
        """
        Rewrites the paths starting with "/" of each page file (links, images, src and href
        attributes). A page that is not a UTF-8 file stops the build, naming the page.
        """
        for page_file in page_files:
            self._rewrite_paths_in_file(page_file)


    # -- Private: one page file ----------------------------------------------------------------------

    def _rewrite_paths_in_file(self, page_file: Path) -> None:
        page_text: str = self._read_page_text(page_file)
        page_text_with_rewritten_paths: str = self._page_text_with_rewritten_paths(page_text, page_file)
        if page_text_with_rewritten_paths != page_text:
            page_file.write_bytes(page_text_with_rewritten_paths.encode("utf-8"))


    @staticmethod
    def _read_page_text(page_file: Path) -> str:
        try:
            return page_file.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise SystemExit(f"{page_file}: the page is not a UTF-8 file")


    def _page_text_with_rewritten_paths(self, page_text: str, page_file: Path) -> str:
        lines: list[str] = page_text.split("\n")
        inside_code_block: bool = False

        for line_index, line in enumerate(lines):
            if CODE_BLOCK_MARKER.match(line):
                inside_code_block = not inside_code_block
            elif not inside_code_block:
                lines[line_index] = self._line_with_rewritten_paths(line, page_file)

        return "\n".join(lines)


    # -- Private: one line ---------------------------------------------------------------------------

    def _line_with_rewritten_paths(self, line: str, page_file: Path) -> str:
        line_with_rewritten_paths: str = ""
        end_of_previous_path: int = 0

        for match in PATH_STARTING_WITH_SLASH.finditer(line):
            resolved_path: str = self.path_resolver.resolve(match["link_path_without_first_slash"], page_file)
            text_before_path: str = line[end_of_previous_path:match.start()]
            line_with_rewritten_paths += text_before_path + match["opening"] + resolved_path
            end_of_previous_path = match.end()

        return line_with_rewritten_paths + line[end_of_previous_path:]
