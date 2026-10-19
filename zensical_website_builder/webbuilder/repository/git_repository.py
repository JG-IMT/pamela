"""
The git operations of the tool, run with the git command of the machine: cloning one version of a
repository at its git reference, deleting that clone, and finding the root of the repository around
a folder. A failure stops the build with one line, naming what failed.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path


class GitRepository:
    """Git operations on a repository: cloning it at a git reference, finding the root of the one around a folder."""

    # -- Public: initialization ----------------------------------------------------------------------

    def __init__(self, repository_url: str) -> None:
        self._repository_url: str = repository_url  # an address, or a folder on this machine


    # -- Public: clone, delete and root --------------------------------------------------------------

    def clone_at(self, git_ref: str, destination_folder: Path) -> None:
        """Clones only the latest state of a branch or a tag (shallow), which is all the build needs."""
        result: subprocess.CompletedProcess = self._run_git(
            ["clone", "--quiet", "--depth", "1", "--branch", git_ref, self._repository_url, str(destination_folder)]
        )
        if result.returncode != 0:
            raise SystemExit(f"Cannot clone {self._repository_url} at '{git_ref}': {result.stderr.strip()}")


    @staticmethod
    def delete_folder_with_clones(folder: Path) -> None:
        """
        Deletes a clone, or a folder holding clones: git writes read-only files in a clone, which
        Windows refuses to delete as they are.
        """
        if folder.exists():
            shutil.rmtree(folder, onerror=GitRepository._retry_after_making_writable)


    @staticmethod
    def find_repository_root_containing(folder: Path) -> Path:
        git_arguments: list[str] = ["-C", str(folder), "rev-parse", "--show-toplevel"]
        result: subprocess.CompletedProcess = GitRepository._run_git(git_arguments)
        if result.returncode != 0:
            raise SystemExit(f"{folder} is not inside a git repository")
        return Path(result.stdout.strip())


    # -- Private: git --------------------------------------------------------------------------------

    @staticmethod
    def _run_git(arguments: list[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(["git", "-c", "core.longpaths=true"] + arguments, capture_output=True, text=True)
        except FileNotFoundError:
            raise SystemExit("git is not installed or not in the PATH")


    @staticmethod
    def _retry_after_making_writable(delete_function, path: str, _error) -> None:
        os.chmod(path, stat.S_IWRITE)
        delete_function(path)
