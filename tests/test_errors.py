"""Direct exercise of the error classes and their messages."""

from __future__ import annotations

from jsonptr import (
    InvalidPointerError,
    JsonPointerError,
    ResolutionError,
)
from jsonptr._errors import format_path


def test_invalid_pointer_error_attributes() -> None:
    err = InvalidPointerError("/foo~", "dangling")
    assert err.pointer == "/foo~"
    assert err.detail == "dangling"
    assert "dangling" in str(err)
    assert isinstance(err, JsonPointerError)
    assert isinstance(err, ValueError)


def test_resolution_error_attributes() -> None:
    err = ResolutionError("/foo/bar", ("foo",), "bar", "missing")
    assert err.pointer == "/foo/bar"
    assert err.path == ("foo",)
    assert err.token == "bar"
    assert err.detail == "missing"
    assert "missing" in str(err)
    assert "'/foo'" in str(err)


def test_resolution_error_allows_none_token() -> None:
    err = ResolutionError("", (), None, "no go")
    assert err.token is None
    assert err.path == ()


def test_format_path_round_trip() -> None:
    assert format_path(()) == ""
    assert format_path(("foo",)) == "/foo"
    assert format_path(("a/b", "c~d")) == "/a~1b/c~0d"
