# Website builder

Builds a documentation website from the Markdown of a repository, with [Zensical](https://zensical.org).
Needs Python 3.11 or later.

## Structure

```
pamela_website/             belongs to Pamela
└─ website_settings.yml        name, menu, links, Markdown folders, previous versions

zensical_website_builder/   the tool, the same for every repository
├─ prepare_website_build.py
├─ shared_site_settings.yml    theme, footer
├─ shared_html_templates/
└─ shared_style_and_icon/

build/website/              generated: input/, zensical_config.yml, output/ (the website)
```

To document another repository, write its own `website_settings.yml` and run the same tool.

## Build

```bash
./gradlew buildDocumentationSite
```

The website is written to `build/website/output`.

## Preview

From `zensical_website_builder/`. Run the 4th command again after editing a Markdown file.

```powershell
python -m venv .venv                                # once
.venv\Scripts\Activate.ps1                          # each terminal (Linux, macOS: source .venv/bin/activate)
pip install -r requirements.txt                     # once
python prepare_website_build.py --settings ../pamela_website/website_settings.yml --build-folder ../build/website
zensical serve -f ../build/website/zensical_config.yml
```

Open http://localhost:8000. Without `--version` the navbar shows "dev".

## Versions

The version menu reads `versions.json`: the current version (`--version`, which Gradle sets from
the project version), then the `previous_versions` of `website_settings.yml`. Previous versions are
not rebuilt, the menu links to where they are published.
