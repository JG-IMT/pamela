# Pamela documentation website

Builds the Pamela website (menu, pages, search) from the Markdown kept in this repository,
using [Zensical](https://zensical.org). Python 3.9+ is the only prerequisite.

## Preview it locally

```bash
cd website
python -m venv .venv                            # once
.venv/Scripts/pip install -r requirements.txt   # once (Linux/macOS: .venv/bin/pip)
.venv/Scripts/python assemble_documentation.py
.venv/Scripts/zensical serve                    # http://localhost:8000
```

Re-run `assemble_documentation.py` after editing a Markdown file (the server can stay up):
Zensical only watches the assembled copy, not the sources.

For a production build use `assemble_documentation.py --clean`, so a page deleted from the
repository cannot linger in the site.

`zensical build` writes the static site to `build/site/`. Both `build/` folders are generated
and ignored by git.

## Where things live

| To change...                  | Edit                                         |
|-------------------------------|----------------------------------------------|
| A page's content              | its `.md` under a `src/site/markdown/` folder |
| Menu order, section names     | `nav:` in `mkdocs.yml`                       |
| Which folders feed the site   | `SOURCE_TO_DESTINATION` in `assemble_documentation.py` |
| Colours, favicon              | `brand/`                                     |
| Version, top links, footer    | `extra:` in `mkdocs.yml`                     |
| Navbar, footer, Previous/Next | `template_overrides/`                        |
