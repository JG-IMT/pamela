# Website builder

Builds a documentation website, with all its versions, from the Markdown of a repository, using
[Zensical](https://zensical.org).

## Install (once)

Needs Python 3.11 or later and git.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Linux and macOS: `source .venv/bin/activate`.

## Build your website

1. Copy `examples/website_settings.yml` into your repository and adapt it (it is commented).
2. Build, then open http://localhost:8000:

```powershell
python main.py build --settings path\to\website_settings.yml
python main.py serve --settings path\to\website_settings.yml
```

The website is in the `build\output` folder next to `website_settings.yml`.

## Settings

In `website_settings.yml`, under `extra:`:

```yaml
repository_url: https://github.com/my_organization/my_project.git
versions:
  - name: "2.0"
    git_ref: "2.0"      # a branch or a tag
    is_latest: true     # exactly one version
  - name: "1.0"
    git_ref: "1.0"
documentation_sources:  # folders of the repository holding the Markdown and the images
  - source: src/site/markdown
    destination: .
```

The latest version is served at `site_url`, the others in `site_url/<name>/`. Quote `name` and
`git_ref`. If something is wrong, the build stops and says what.

## Good to know

- `build` reads git: commit and push your work first, or add `--repository-url <your folder>`.
- To preview your Markdown while writing, without building the other versions:

```powershell
python main.py prepare --settings path\to\website_settings.yml
zensical serve -f path\to\build\zensical_config.yml
```

- Links starting with `/` are fixed in the build, the Markdown of your repository is not changed.
