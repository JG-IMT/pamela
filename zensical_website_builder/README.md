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

Run everything from `zensical_website_builder/`.

**1. Create the environment (once).** Skip it if `./gradlew buildDocumentationSite` already ran:
it creates `.venv`.

```bash
python -m venv .venv
```

**2. Activate it (each new terminal).**

```powershell
.venv\Scripts\Activate.ps1      # Windows PowerShell
```

```bash
source .venv/bin/activate       # Linux, macOS
```

**3. Install Zensical (once).**

```bash
pip install -r requirements.txt
```

**4. Prepare the website files.** Run it again after editing a Markdown file: Zensical only
watches its input folder, not the repository. Without `--version` the navbar shows "dev".

```bash
python prepare_website_build.py --settings ../pamela_website/website_settings.yml --build-folder ../build/website
```

**5. Start the server** and open http://localhost:8000. It can stay up between two runs of step 4.

```bash
zensical serve -f ../build/website/zensical_config.yml
```

For a production build, add `--clean` to step 4 so that a page deleted from the repository
cannot linger.
