# Documentation website

Builds a documentation website (menu, pages, search) from the Markdown kept in a repository,
using [Zensical](https://zensical.org). Prerequisite: Python 3.11 or later.

The tooling is meant to be reusable. Every Openflexo site shares the same look (`site_style.css`,
`template_overrides/`). Only these files are specific to Pamela: `mkdocs.yml` (name, menu, links,
documentation sources), the logo and `favicon.ico`.

## Preview it locally

Run these from this folder.

```bash
python -m venv .venv                            # once
.venv/Scripts/pip install -r requirements.txt   # once (Linux/macOS: .venv/bin/pip)
.venv/Scripts/python prepare_zensical_input.py mkdocs.yml
.venv/Scripts/zensical serve                    # http://localhost:8000
```

Re-run `prepare_zensical_input.py` after editing a Markdown file (the server can stay up):
Zensical only watches its input folder, not the repository.

For a production build use `prepare_zensical_input.py mkdocs.yml --clean`, so that a page
deleted from the repository cannot linger, then `zensical build`.

## Build it with Gradle

From the repository root. This is what Jenkins runs as well.

```bash
./gradlew buildDocumentationSite
```

The website is written to `zensical_website_builder/build/zensical_output`. The task chain:

| Task | What it does |
|---|---|
| `setupDocumentationEnvironment` | creates `.venv` and installs Zensical, only if `.venv` is missing |
| `prepareDocumentationInput` | runs `prepare_zensical_input.py mkdocs.yml --clean` |
| `buildDocumentationSite` | runs `zensical build` and shows the Gradle project `version` in the navbar |

Built by hand, the navbar shows "dev": the version comes from the `PROJECT_VERSION` environment
variable that the Gradle task sets.

## How the folders relate


1. repository (Markdown, images) : prepare_zensical_input.py copies the folders listed in extra.documentation_sources.
      
2. build/zensical_input/ : what Zensical reads zensical when typing  `.venv/Scripts/zensical serve`.
      
3. build/zensical_output/ : the website resulted by `.venv/Scripts/zensical serve`.


Both `build/` folders are generated and ignored by git.
