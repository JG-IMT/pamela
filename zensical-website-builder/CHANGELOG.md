# Changelog

All notable changes to this tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] 22/10/2026

### Added

- The README describes the structure of the tool, file by file, and the folders a build creates.

### Changed

- The settings shared by every website are in `shared/default_settings.yml` (it was `shared/site_settings.yml`)
  and the settings of the project override them.
- The code follows one structure: the classes keep their data private, the settings, the version and the
  catalog of versions give it through `get_*` methods, a version and the catalog of versions are two classes
  in two files, and folders are copied and deleted by one helper.

## [0.0.0] 20/10/2026

Initial development version.

### Added

- Builds the documentation website of a project from the Markdown of its git repository, with
  Zensical: `python main.py --settings website_settings.yml`.
- Several versions per website, each one cloned from a branch or a tag. The latest version is served at
  the root of the website, the others in a folder named after them.
- One `website_settings.yml` per project, completed by the settings shared by every website.
- URLs starting with `/` are rewritten in the copies of the Markdown pages.
- A build that fails keeps the previous website, and the clones are deleted once each version is built.
