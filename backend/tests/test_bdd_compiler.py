import sys
from pathlib import Path

from pytest_bdd import given, scenarios, then, when

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.compiler import compile_manifest

scenarios("features/compiler.feature")


@given("config sources that disagree on the package manager", target_fixture="sources")
def sources():
    return [
        {"name": ".cursorrules", "content": "Use pnpm for package operations."},
        {"name": "CLAUDE.md", "content": "Install packages with npm only."},
    ]


@when('I compile the sources with "npm" selected', target_fixture="result")
def compile_sources(sources):
    return compile_manifest(sources, {"packageManager": "npm"})


@then('the manifest uses "npm" for package operations')
def manifest_uses_npm(result):
    assert "Use npm for all package operations." in result["manifest"]
