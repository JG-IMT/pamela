from pathlib import Path

TOOL_FOLDER: Path = Path(__file__).resolve().parents[1]
SHARED_FOLDER: Path = TOOL_FOLDER / "shared"
SHARED_SETTINGS_FILE: Path = SHARED_FOLDER / "site_settings.yml"
SHARED_STYLE_AND_ICON_FOLDER: Path = SHARED_FOLDER / "style_and_icon"
SHARED_HTML_TEMPLATES_FOLDER: Path = SHARED_FOLDER / "html_templates"
