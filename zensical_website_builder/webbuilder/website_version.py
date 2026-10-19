import re

VERSION_NAME_PATTERN: re.Pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


class WebsiteVersion:
    """A version of the documentation: the git reference it is built from, and optionally its own menu."""

    def __init__(self, declaration: dict):
        self.name: str = self._required_text(declaration, "name")
        self.git_ref: str = self._required_text(declaration, "git_ref")
        self.is_latest: bool = bool(declaration.get("is_latest", False))
        self.navigation: list | None = declaration.get("navigation")
        if not VERSION_NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"version name '{self.name}' may only contain letters, digits, '.', '_' and '-'")

    # -- Private: declaration -----------------------------------------------------------

    @staticmethod
    def _required_text(declaration: dict, key: str) -> str:
        value = declaration.get(key)
        if not isinstance(value, str):
            raise ValueError(f"version {declaration}: '{key}' is required and must be text (quote it: \"1.6\")")
        return value
