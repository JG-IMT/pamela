# Documentation website

Builds a documentation website (menu, pages, search) from the Markdown kept in a repository,
using [Zensical](https://zensical.org). Prerequisite: Python 3.11 or later.

The tooling is meant to be reusable: only the files listed under "What belongs to the project"
are specific to Pamela.

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

## How the folders relate


1. repository (Markdown, images) : prepare_zensical_input.py copies the folders listed in extra.documentation_sources.
      
2. build/zensical_input/ : what Zensical reads zensical when typing  `.venv/Scripts/zensical serve`.
      
3. build/zensical_output/ : the website resulted by `.venv/Scripts/zensical serve`.


Both `build/` folders are generated and ignored by git.
