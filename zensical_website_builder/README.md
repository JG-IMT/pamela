# Website builder

Builds a documentation website (menu, pages, search) from the Markdown kept in a repository,
using [Zensical](https://zensical.org). Prerequisite: Python 3.11 or later.

## Who owns what

```
pamela_website/                  1. Belongs to Pamela (you write it)
└─ website_settings.yml             name, menu, links, folders holding the Markdown, logo

zensical_website_builder/        2. The tool (the same for every repository)
├─ prepare_website_build.py
├─ shared_site_settings.yml         theme, palette, extensions, footer
├─ shared_html_templates/           header, footer, pagination
├─ shared_style_and_icon/           site_style.css, favicon.ico
└─ requirements.txt

build/website/                   3. Generated (ignored by git)
├─ input/                           the Markdown copied here, read by Zensical
├─ zensical_config.yml              shared settings completed by Pamela's
└─ output/                          the website
```

Every Openflexo website shares the same look. To document another repository, create its own
folder with a `website_settings.yml` (copy Pamela's) and run the same tool on it.

## Build it with Gradle

From the repository root. This is what Jenkins runs as well.

```bash
./gradlew buildDocumentationSite
```

The website is written to `build/website/output`. The task chain:

| Task | What it does |
|---|---|
| `setupDocumentationEnvironment` | creates `.venv` and installs Zensical, only if `.venv` is missing |
| `prepareDocumentationInput` | runs `prepare_website_build.py`: copies the Markdown, generates the Zensical config |
| `buildDocumentationSite` | runs `zensical build` |

The version in the navbar is the Gradle project `version`.

## Preview it locally

Run these from this folder, once Gradle has created `.venv` (or create it by hand:
`python -m venv .venv`, then `.venv/Scripts/pip install -r requirements.txt`; on Linux and macOS
use `.venv/bin`).

```bash
.venv/Scripts/python prepare_website_build.py --settings ../pamela_website/website_settings.yml --build-folder ../build/website
.venv/Scripts/zensical serve -f ../build/website/zensical_config.yml    # http://localhost:8000
```

Re-run the first command after editing a Markdown file (the server can stay up): Zensical only
watches its input folder, not the repository. Without `--version` the navbar shows "dev".

For a production build add `--clean` to the first command, so that a page deleted from the
repository cannot linger.
