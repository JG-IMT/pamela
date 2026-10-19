import subprocess
from pathlib import Path


class GitRepository:
    """A git repository, cloned to build one of its versions."""

    def __init__(self, repository_url: str):
        self.repository_url: str = repository_url

    # -- Public: clone and root ---------------------------------------------------------

    def clone_at(self, git_ref: str, destination_folder: Path) -> None:
        result: subprocess.CompletedProcess = self._run_git(
            ["clone", "--quiet", "--depth", "1", "--branch", git_ref, self.repository_url, str(destination_folder)]
        )
        if result.returncode != 0:
            raise SystemExit(f"Cannot clone {self.repository_url} at '{git_ref}': {result.stderr.strip()}")

    @staticmethod
    def find_root_containing(folder: Path) -> Path:
        result: subprocess.CompletedProcess = GitRepository._run_git(["-C", str(folder), "rev-parse", "--show-toplevel"])
        if result.returncode != 0:
            raise SystemExit(f"{folder} is not inside a git repository")
        return Path(result.stdout.strip())

    # -- Private: git -------------------------------------------------------------------

    @staticmethod
    def _run_git(arguments: list) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(["git", "-c", "core.longpaths=true"] + arguments, capture_output=True, text=True)
        except FileNotFoundError:
            raise SystemExit("git is not installed or not in the PATH")
