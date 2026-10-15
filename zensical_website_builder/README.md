# Website builder

Builds a documentation website from the Markdown of a repository, with [Zensical](https://zensical.org).
The same tool, theme and footer for every repository: each one only brings a `website_settings.yml`.

## Install (once)

Python 3.11 to 3.13 is required (3.14 and later do not work yet).

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux and macOS: `source .venv/bin/activate`. If PowerShell blocks the script, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.

## Use

For a new repository, copy `examples/website_settings.yml` and adapt it. Then:

```powershell
python main.py prepare --settings ..\my_site\website_settings.yml --version 1.6.1
zensical build --clean -f ..\my_site\build\zensical_config.yml
```

Everything is generated in the `build` folder next to `website_settings.yml`; the website is in
`build\output`. To preview it on http://localhost:8000, replace the second command by:

```powershell
zensical serve -f ..\my_site\build\zensical_config.yml
```

## Features

**Links starting with "/"** (e.g. `![](/images/a.png)`) break under `openflexo.org/<project>/docs/`.
`prepare` fixes them in its copy of the pages, the Markdown of the repository is not changed:

- the target is in the website: the link becomes relative (declare its folder in `documentation_sources`)
- the link already starts with the project path (`/my_project/javadoc/...`): unchanged
- otherwise the project path is put in front (`/javadoc/...` becomes `/my_project/javadoc/...`)

The project path comes from `homepage` in `website_settings.yml`.

**Versions**: the menu lists the version being built, then the `previous_versions` of
`website_settings.yml`. To build an earlier version, name the latest one: every page then shows a
banner linking to it.

```powershell
python main.py prepare --settings ..\my_site\website_settings.yml --version 1.6 --latest-version 1.6.1
```

**Global search**: to also find the pages of other Openflexo websites, declare them under
`global_search` in `website_settings.yml`, then run after `zensical build`:

```powershell
python main.py search --settings ..\my_site\website_settings.yml
```

The websites must share the same domain; one that cannot be reached is skipped with a warning.
