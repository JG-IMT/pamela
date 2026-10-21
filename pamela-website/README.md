# Pamela documentation website

The website of Pamela, with all its versions, is built from the Markdown of this git repository.
`website_settings.yml` says which versions are built, from which branches or tags, and which folders hold
the documentation.

## Build and view

Python 3.11 or later and git are needed. From the root of the repository:

```bash
./gradlew buildDocumentationSite
./gradlew serveDocumentationSite
```

The first command builds every version in `pamela-website/build/website`, the second serves it: open
http://localhost:8000. The first build creates the Python environment and installs Zensical. On Windows, use
`gradlew.bat`.

## Change the versions

Edit `extra.versions` in `website_settings.yml`. Each version has a `name`, a branch or a tag (`git_ref`),
and exactly one of them is `is_latest: true`. The versions must be pushed: the build reads them from git.

## More

The website builder is in `zensical-website-builder/`, see its README.
