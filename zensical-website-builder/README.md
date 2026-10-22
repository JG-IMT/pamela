# Website builder

Builds the documentation website of an OpenFlexo project (Pamela, Connie, ...), with all its versions,
from the Markdown of its git repository, using [Zensical](https://zensical.org). The tool, the theme and
the OpenFlexo footer are the same for every project: a project only brings a `website_settings.yml`.

## What a project needs

- a git repository holding its documentation as Markdown files.
- a `website_settings.yml` saying where the documentation is, which versions to build and how the website
  looks. Start from `examples/website_settings.yml`.

## Install (once)

Needs Python 3.11 or later and git.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux and macOS: `source .venv/bin/activate`.

## Build

```powershell
python main.py --settings path\to\website_settings.yml
```

`--settings` is the path of the `website_settings.yml` of the project (required). Every version it
declares is cloned from git and built. The website is in the `build\website` folder next to
`website_settings.yml`: the latest version at its root, each earlier version in a folder named after it.
To look at it, serve that folder with any web server, for example
`python -m http.server 8000 --directory build\website`, then open http://localhost:8000.

## Settings

| Key | Role |
|---|---|
| `site_name` | Name of the website |
| `site_description` | One sentence describing the project |
| `site_url` | Address where the website is published. The latest version is served there, the others in `site_url/<name>/` |
| `theme.logo` | Logo of the website: a path inside the website, or an address |
| `extra.repository_url` | The git repository to clone |
| `extra.versions` | The versions to build. For each one: `name` (shown in the menu, used as folder name), `git_ref` (a branch or a tag), `is_latest: true` (on exactly one version) and an optional `navigation` (the menu; without it the menu is generated from the pages) |
| `extra.documentation_sources` | The folders of the repository copied into the website. `source` is relative to the repository root, `destination` is the folder in the website (`.` for its root). A later entry overwrites an earlier one |
| `extra.homepage` | Home page of the project. Its path completes the URLs starting with `/` that lead outside the website (`/javadoc/...` becomes `/<path>/javadoc/...`) |
| `extra.navbar_links` | The links of the top bar |

## Structure of the tool

```text
Zensical-WebBuilder/
├── main.py                              Starts the build of the website described by --settings
├── requirements.txt                     Python dependencies
├── CHANGELOG.md
├── examples/
│   └── website_settings.yml             Template for a project
├── shared/                              Common to every website
│   ├── default_settings.yml             Common settings every website starts from
│   ├── html_templates/                  Overrides of the theme pages
│   │   ├── main.html                    Version badge and "no longer maintained" banner
│   │   └── partials/                    header, navbar_links, version_menu, copyright
│   └── style_and_icon/                  site_style.css and favicon.ico
└── webbuilder/                          The code
    ├── shared_paths.py                  Locations of the files of shared/
    ├── settings/
    │   ├── website_settings.py          Reads website_settings.yml over the shared settings and checks it
    │   ├── website_version.py           One declared version: name, git reference, latest or not, menu; checked
    │   └── website_version_catalog.py   The versions: checks them together, gives each one its folder and address
    ├── helper/
    │   └── folder_helper.py             Copies and deletes folders (the only use of shutil)
    ├── repository/
    │   └── git_repository.py            Clones a branch or a tag
    ├── preparation/                     Converts a clone to a structure read by Zensical
    │   ├── zensical_input.py            Copies the sources, then writes the menu of versions and Zensical config
    │   ├── page_url_rewriter.py         Rewrites the URLs starting with "/" in the pages
    │   └── page_url_resolver.py         Decides what one such URL becomes
    └── building/
        ├── version_build.py             One version: clone, preparation, Zensical
        └── website_build.py             All versions, assembled into build/website
```

After building, a build folder is created next to `website_settings.yml`:

```text
build/
├── version_builds/<version>/          Kept after the build to see what Zensical was given and produced
│   ├── zensical_input/                Sources copied and rewritten
│   ├── zensical_config.yml            Configuration given to Zensical
│   └── version_site/                  Site built by Zensical (the clone is deleted)
└── website/                           Result: latest version at the root, the others in <version>/
```

## Good to know

- The build reads git.
- Links starting with `/` that lead to a file of the documentation are made relative in the build; the
  Markdown of your repository is not changed.
- A build that fails keeps the previous website.
