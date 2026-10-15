# Changelog of the documentation website

Changes made to this repository (branch `julien-clean`, from `1.6.1`) to build the documentation
website with the Zensical website builder, on 2026-10-15.

## Added

- `zensical_website_builder/`: copy of the website builder (19 files). It is the same tool for every
  Openflexo repository; this copy is kept in sync by hand.
- `pamela_website/website_settings.yml`: everything specific to Pamela: site name, menu (`nav`),
  folders holding the Markdown (`src/site/markdown`, `pamela-core/src/site/markdown`,
  `pamela-security-patterns/src/site/markdown`), folders of images and files (`src/site/resources/images`,
  `img`, `examples`), previous versions (`1.6`, `1.5.0.1`) and links of the top bar.
- `build.gradle`: block "Documentation website (Zensical)" with four tasks:
  `createDocumentationEnvironment`, `installDocumentationTools`, `prepareDocumentationInput`,
  `buildDocumentationSite`.
- `pamela_website/CHANGELOG.md` and `pamela_website/KNOWN_ISSUES.md` (these two files).

## Not changed

No Markdown page, image or file of the documentation was modified or moved. The links starting with
`/` (`/images/...`, `/img/...`, `/examples/...`) are fixed by the builder in its own copy of the
pages, not in this repository.

## How to build

```powershell
.\gradlew.bat buildDocumentationSite
```

The website is written to `pamela_website/build/output` (ignored by Git). Details and options of the
builder: `zensical_website_builder/README.md`.

## Checked

- Latest version (`1.6.1`): 29 pages, 20 links fixed, 0 broken link out of 1,377.
- Earlier versions rebuilt from their branches: `1.6` (29 pages) and `1.5.0.1` (7 pages), with the
  banner pointing to the latest version. Menus, banners and 2,896 internal links of the three
  assembled versions checked, 0 broken.
- The menu and the pages match those of the Docusaurus website (`openflexo.org/pamela/docs/`),
  except for the version label (`1.6.1` here, `1.6.1-java-11` there).
