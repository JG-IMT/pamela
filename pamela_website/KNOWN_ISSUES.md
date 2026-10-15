# Known issues and next steps (Pamela documentation website)

State on 2026-10-15, branch `julien-clean`. The issues of the builder itself are in
`zensical_website_builder/KNOWN_ISSUES.md` of the Zensical-WebBuilder repository.

## Build

- **Gradle needs a JDK** (a JRE alone fails on `compileJava`). JDK 8 is installed.
- **Gradle takes `python` from the PATH.** With Python 3.14 or later and no
  `zensical_website_builder/.venv`, the installation fails: create `.venv` with Python 3.12 first.
- **Gradle 8.14 warnings** that are not ours: running on Java 16 or lower is deprecated, and
  `url uri(...)` in `buildscript` (lines 68 and 79 of `build.gradle`).
- **Nothing publishes the website.** The old `buildWebsite` task (Docusaurus, `scp` to
  `openflexo.org`, javadoc) is still in a commented block at the top of `build.gradle`.

## Documentation content

- `getting_started.md` (1.6.1): the sentence "The javadoc for Pamela can be found ." has lost its
  link (it is `[here](/javadoc/pamela-core/index.html)` in `1.6`).
- Every page of `pamela-core` and `pamela-security-patterns` keeps a Docusaurus header
  (`sidebar_position`). Zensical ignores it without error; it can be removed later.
- Maven leftovers are still in the repository and unused by the website: `src/site/site.xml`,
  `src/site/xdoc/`, `pamela-core/src/site/site.xml`, `pamela-security-patterns/src/site/site.xml`.
- The images exist twice in `src/site/resources` (at the root and in `images/`, same files). Only
  `images/`, `img/` and `examples/` are used.
- The menu (`nav`) lists every page: a new page must be added to `website_settings.yml`.

## Versions

- `previous_versions` links point to the Docusaurus copies published on `openflexo.org`. They are
  not rebuilt by this repository.
- Earlier versions can be built from the branches `1.6` and `1.5.0.1` (checked), but each one needs a
  settings file (the menu of `1.5.0.1` is limited to its 7 pages): they are not in the repository yet.
  The branches `1.5.1` and `1.5` have one page.
- The label is `1.6.1` (the version of `build.gradle`); the Docusaurus website shows `1.6.1-java-11`.

## Next steps

1. Re-copy `zensical_website_builder/` whenever the builder changes (manual copy for now; later
   `pip install` from GitHub with a tag).
2. Two Gradle commands for all versions (`buildDocumentationSite`, `serveDocumentationSite`): needs
   the builder's `build` command and the decision on where the imported earlier versions live
   (`pamela_website/versions/` or outside the repository).
3. Decide whether to clean the Maven leftovers, the duplicated images and the Docusaurus headers
   (changes to Pamela's reference structure).
4. Publishing of the website and of the javadoc.
