"""
Decides where a path starting with "/" must point once the Markdown pages are in the website. Such a
path leads to the root of the domain, not to the root of the website, so it needs fixing. It knows the
folder holding the pages of the website and the project URL path, nothing about how the pages are read
or written.
"""

import posixpath
import re
from pathlib import Path
from urllib.parse import unquote


class WebsitePathResolver:
    """Decides where a path starting with "/" must point once the Markdown pages are in the website."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, input_folder: Path, project_url_path: str = "") -> None:
        self.input_folder: Path = input_folder
        self.project_url_path: str = project_url_path

        self._reported_guesses: set[tuple[Path, str]] = set()  # one warning per guessed path and per page


    # -- Public: entry point -------------------------------------------------------------------------

    def resolve(self, link_path_without_first_slash: str, page_file: Path) -> str:
        """
        Returns the path as it must be written in the page:
          1. the target is in the website: the path becomes relative to the page
          2. the path already starts with the project URL path (/my_project/javadoc/...): unchanged
          3. otherwise the project URL path is put in front (/javadoc/... becomes /my_project/javadoc/...),
             and a warning names the page and the path, once
        """
        if self._target_is_in_website(link_path_without_first_slash):
            return self._relative_to_page(link_path_without_first_slash, page_file)
        if self._is_already_complete(link_path_without_first_slash):
            return "/" + link_path_without_first_slash
        return self._guess_with_project_url_path(link_path_without_first_slash, page_file)


    # -- Private: the three cases --------------------------------------------------------------------

    def _target_is_in_website(self, link_path_without_first_slash: str) -> bool:
        link_path_without_fragment_or_query: str = re.split(r"[#?]", link_path_without_first_slash)[0]
        target_path: str = unquote(link_path_without_fragment_or_query)  # "my%20image.png" is the file "my image.png"
        return (self.input_folder / target_path).exists()


    def _relative_to_page(self, link_path_without_first_slash: str, page_file: Path) -> str:
        page_folder: str = page_file.parent.relative_to(self.input_folder).as_posix()
        return posixpath.relpath(link_path_without_first_slash, start=page_folder)


    def _is_already_complete(self, link_path_without_first_slash: str) -> bool:
        return not self.project_url_path or link_path_without_first_slash.startswith(self.project_url_path + "/")


    def _guess_with_project_url_path(self, link_path_without_first_slash: str, page_file: Path) -> str:
        link_path_with_project_url_path: str = f"/{self.project_url_path}/{link_path_without_first_slash}"
        self._report_guess_once(link_path_without_first_slash, link_path_with_project_url_path, page_file)
        return link_path_with_project_url_path


    # -- Private: warning ----------------------------------------------------------------------------

    def _report_guess_once(self, link_path_without_first_slash: str, guessed_path: str, page_file: Path) -> None:
        guess: tuple[Path, str] = (page_file, link_path_without_first_slash)
        if guess in self._reported_guesses:
            return
        self._reported_guesses.add(guess)

        page_path_in_website: str = page_file.relative_to(self.input_folder).as_posix()
        original_link_path: str = "/" + link_path_without_first_slash
        print(f"Warning: {page_path_in_website}: {original_link_path} treated as {guessed_path}")
