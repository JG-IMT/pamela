# Website builder

Builds a documentation website from the Markdown of a repository, with [Zensical](https://zensical.org).
Needs Python 3.11 to 3.13 (3.14 and later: PyYAML and Zensical do not install yet).

## Structure

```
website_settings.yml        belongs to each repository: name, menu, links, Markdown folders, previous versions

Zensical-WebBuilder/        the tool, the same for every repository
├─ main.py                     entry point: "prepare" and "search" commands
├─ requirements.txt
├─ webbuilder/
│  ├─ website_settings.py      WebsiteSettings: shared settings completed by the project's
│  ├─ website_input.py         WebsiteInput: input folder and config read by Zensical
│  ├─ markdown_links.py        MarkdownLinks: links starting with "/" made relative
│  └─ search_index.py          SearchIndex: search.json, with the pages of other websites
├─ shared/
│  ├─ site_settings.yml        theme, footer
│  ├─ html_templates/
│  └─ style_and_icon/
└─ examples/
   └─ website_settings.yml     template to copy for a new repository

build/                      generated next to website_settings.yml: input/, zensical_config.yml, output/ (the website)
```

To document another repository, copy `examples/website_settings.yml`, adapt it and run the same tool.

## Build

From the tool folder, once:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # each terminal (Linux, macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Then, with `<website folder>` the folder holding the `website_settings.yml` of the repository:

```powershell
python main.py prepare --settings <website folder>\website_settings.yml --version <version>
zensical build --clean -f <website folder>\build\zensical_config.yml
```

For example, with `..\my_project_website\website_settings.yml`, the config is
`..\my_project_website\build\zensical_config.yml` (the folder, not the file, followed by `build`).
Everything generated goes to this `build` folder, and the website is written to `build\output`. A repository can run these commands from its own build (a Gradle task,
for example).

## Preview

Replace the last command above by the following one, and run the `main.py prepare` command
again after editing a Markdown file.

```powershell
zensical serve -f <website folder>\build\zensical_config.yml
```

Open http://localhost:8000. Without `--version` the navbar shows "dev".

## Links starting with "/"

A link such as `![](/images/schema.png)` leads to the root of the domain, so it breaks once the
website is published under `openflexo.org/<project>/docs/` (typical of Markdown written for
Docusaurus). `main.py prepare` makes these links relative in the copies of the pages (Markdown links
and `src="/..."` / `href="/..."`, except inside code blocks); the Markdown of the repository is not
changed. The target must exist in the website: declare the folder holding it under
`documentation_sources`, with the name the links expect (`images`, `img`, `examples`...).

## Global search

The search box of a website can also find the pages of the other Openflexo websites. Declare them
in `website_settings.yml` (see `examples/website_settings.yml`), then, after `zensical build`:

```bash
python main.py search --settings <website_settings.yml>
```

The `search.json` of the other websites is downloaded when the script runs. A website that cannot be
reached is skipped with a warning.

Limitation: the websites must share the same domain (for example `openflexo.org/<project_a>/docs/` and
`openflexo.org/<project_b>/docs/`). The search box opens its results relative to the current website, so
a website on another domain is skipped with a warning.

## Versions

The version menu reads `versions.json`: the current version (`--version`, set by the build of the
repository), then the `previous_versions` of `website_settings.yml`. Previous versions are
not rebuilt, the menu links to where they are published.
