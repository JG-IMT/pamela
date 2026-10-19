"""
Entry point of the website builder.

Usage:
    python main.py prepare --settings <website_settings.yml> [--clean]
        Prepares what Zensical needs to preview the latest version: the input folder (the Markdown and
        images of the repository containing website_settings.yml, as they are now, plus the files shared
        by every website) and the config file. Everything generated goes to the "build"
        folder next to website_settings.yml. Then build with:
        zensical build -f <build folder>/zensical_config.yml

    python main.py build --settings <website_settings.yml> [--repository-url <url or folder>]
        Clones each version declared in website_settings.yml at its git_ref, builds it with Zensical and
        assembles the website in <build folder>/output: the latest version at its root, each earlier
        version in a folder named after it.

    python main.py serve --settings <website_settings.yml> [--port 8000]
        Serves <build folder>/output on http://localhost:<port>/ once the website is built.
"""

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from webbuilder.building.website_build import WebsiteBuild
from webbuilder.preparation.version_site_input import OUTPUT_FOLDER_NAME, VersionSiteInput
from webbuilder.repository.git_repository import GitRepository
from webbuilder.settings.website_settings import WebsiteSettings

BUILD_FOLDER_NAME: str = "build"
DEFAULT_PORT: int = 8000


# -- Commands -------------------------------------------------------------------------------------------

def _prepare(arguments: argparse.Namespace) -> None:
    settings: WebsiteSettings = WebsiteSettings(arguments.settings)
    repository_folder: Path = GitRepository.find_repository_root_containing(arguments.settings.parent)
    build_folder: Path = arguments.settings.parent / BUILD_FOLDER_NAME
    version_site_input: VersionSiteInput = VersionSiteInput(
        settings, repository_folder, build_folder, settings.versions.latest
    )
    print(f"Zensical config: {version_site_input.prepare(arguments.clean)}")


def _build(arguments: argparse.Namespace) -> None:
    settings: WebsiteSettings = WebsiteSettings(arguments.settings)
    git_repository: GitRepository = GitRepository(settings.repository_url_to_clone(arguments.repository_url))
    WebsiteBuild(settings, git_repository, arguments.settings.parent / BUILD_FOLDER_NAME).build()


def _serve(arguments: argparse.Namespace) -> None:
    output_folder: Path = arguments.settings.parent / BUILD_FOLDER_NAME / OUTPUT_FOLDER_NAME
    if not output_folder.is_dir():
        raise SystemExit(f"{output_folder} does not exist: run the build command first")
    request_handler = functools.partial(SimpleHTTPRequestHandler, directory=str(output_folder))
    print(f"Serving {output_folder} on http://localhost:{arguments.port}/ (Ctrl+C to stop)")
    with ThreadingHTTPServer(("localhost", arguments.port), request_handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


# -- Command line ---------------------------------------------------------------------------------------

def _existing_file(argument: str) -> Path:
    file: Path = Path(argument)
    if not file.is_file():
        raise argparse.ArgumentTypeError(f"{file} is not an existing file (expected a website_settings.yml)")
    return file


def _parse_arguments() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Website builder, based on Zensical.")
    commands = parser.add_subparsers(dest="command", required=True)

    prepare_parser = commands.add_parser("prepare", help="prepare the input folder and the config of Zensical")
    prepare_parser.add_argument("--clean", action="store_true", help="delete the input folder first")
    prepare_parser.set_defaults(run=_prepare)

    build_parser = commands.add_parser("build", help="build every declared version and assemble the website")
    build_parser.add_argument("--repository-url", help="repository to clone instead of the declared one")
    build_parser.set_defaults(run=_build)

    serve_parser = commands.add_parser("serve", help="serve the built website on http://localhost")
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve_parser.set_defaults(run=_serve)

    for command_parser in (prepare_parser, build_parser, serve_parser):
        command_parser.add_argument("--settings", type=_existing_file, required=True,
                                    help="website_settings.yml of the project")
    return parser.parse_args()


if __name__ == "__main__":
    arguments: argparse.Namespace = _parse_arguments()
    arguments.run(arguments)
