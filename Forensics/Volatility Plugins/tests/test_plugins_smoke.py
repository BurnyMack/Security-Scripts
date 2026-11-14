"""Static smoke tests for the Volatility plugins.

These are Volatility 2 (Python-2-era) framework plugins: they ``import
volatility.*`` and are loaded into a Volatility install, so they cannot be
imported at runtime under the Python 3.11+ test matrix. Instead we verify each
plugin file statically: it is syntactically valid Python and defines at least
one class (the plugin itself) and a non-trivial header/docstring. This catches
accidental syntax breakage from consistency edits without needing the
framework installed.
"""

import ast
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1]
PLUGINS = sorted(PLUGIN_DIR.glob("*.py"))


def test_plugins_found():
    assert PLUGINS, "expected at least one Volatility plugin .py file"


@pytest.mark.parametrize("path", PLUGINS, ids=lambda p: p.name)
def test_plugin_is_valid_python(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))  # raises SyntaxError on bad syntax
    compile(tree, str(path), "exec")


@pytest.mark.parametrize("path", PLUGINS, ids=lambda p: p.name)
def test_plugin_defines_a_class(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert classes, f"{path.name} defines no plugin class"


@pytest.mark.parametrize("path", PLUGINS, ids=lambda p: p.name)
def test_plugin_has_header_documentation(path):
    # Either a module docstring or a leading comment block describing it.
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    has_docstring = ast.get_docstring(tree) is not None
    has_comment_header = source.lstrip().startswith("#")
    assert has_docstring or has_comment_header, f"{path.name} lacks header documentation"
