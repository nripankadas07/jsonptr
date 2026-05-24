"""Lock down the public API of :mod:`jsonptr`."""

from __future__ import annotations

import jsonptr


def test_api_surface_exports_expected_names() -> None:
    assert set(jsonptr.__all__) == {
        "END_OF_ARRAY",
        "InvalidPointerError",
        "JsonPointerError",
        "ResolutionError",
        "escape",
        "format_pointer",
        "format_uri_fragment",
        "get",
        "has",
        "parse",
        "parse_uri_fragment",
        "remove",
        "resolve",
        "set_value",
        "to_pointer",
        "unescape",
    }


def test_error_hierarchy_is_value_error() -> None:
    assert issubclass(jsonptr.JsonPointerError, ValueError)
    assert issubclass(jsonptr.InvalidPointerError, jsonptr.JsonPointerError)
    assert issubclass(jsonptr.ResolutionError, jsonptr.JsonPointerError)


def test_end_of_array_marker_is_dash() -> None:
    assert jsonptr.END_OF_ARRAY == "-"


def test_version_present() -> None:
    assert isinstance(jsonptr.__version__, str)
    assert jsonptr.__version__.count(".") >= 1


def test_callables_present() -> None:
    for name in (
        "escape",
        "format_pointer",
        "format_uri_fragment",
        "get",
        "has",
        "parse",
        "parse_uri_fragment",
        "remove",
        "resolve",
        "set_value",
        "to_pointer",
        "unescape",
    ):
        assert callable(getattr(jsonptr, name)), name
