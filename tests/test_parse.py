"""Parse / format / escape / unescape (RFC 6901 §3 + §4)."""

from __future__ import annotations

import pytest

from jsonptr import (
    InvalidPointerError,
    escape,
    format_pointer,
    parse,
    to_pointer,
    unescape,
)


# ---------------------------------------------------------------------------
# escape / unescape
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,encoded",
    [
        ("", ""),
        ("foo", "foo"),
        ("foo/bar", "foo~1bar"),
        ("foo~bar", "foo~0bar"),
        ("a/b~c", "a~1b~0c"),
        ("~/", "~0~1"),
        ("/~", "~1~0"),
        ("~1", "~01"),
        ("~01", "~001"),
        ("multi/slash/sep", "multi~1slash~1sep"),
    ],
)
def test_escape_round_trip(raw: str, encoded: str) -> None:
    assert escape(raw) == encoded
    assert unescape(encoded) == raw


def test_escape_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        escape(7)  # type: ignore[arg-type]


def test_unescape_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        unescape(7)  # type: ignore[arg-type]


def test_unescape_rejects_trailing_tilde() -> None:
    with pytest.raises(InvalidPointerError):
        unescape("foo~")


def test_unescape_rejects_unknown_escape() -> None:
    with pytest.raises(InvalidPointerError) as info:
        unescape("foo~2")
    assert "must be followed by '0' or '1'" in str(info.value)


# ---------------------------------------------------------------------------
# parse / format_pointer
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "pointer,tokens",
    [
        ("", ()),
        ("/", ("",)),
        ("/foo", ("foo",)),
        ("/foo/0", ("foo", "0")),
        ("/foo/bar/baz", ("foo", "bar", "baz")),
        ("/a~1b", ("a/b",)),
        ("/m~0n", ("m~n",)),
        ("/m~0n/a~1b", ("m~n", "a/b")),
        ("//", ("", "")),
        ("/foo/", ("foo", "")),
    ],
)
def test_parse_round_trip(pointer: str, tokens: tuple) -> None:
    assert parse(pointer) == tokens
    assert format_pointer(tokens) == pointer


def test_parse_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        parse(7)  # type: ignore[arg-type]


def test_parse_rejects_missing_leading_slash() -> None:
    with pytest.raises(InvalidPointerError) as info:
        parse("foo")
    assert "must begin with '/'" in str(info.value)


def test_parse_rejects_token_with_bad_escape() -> None:
    with pytest.raises(InvalidPointerError):
        parse("/foo~5bar")


def test_parse_rejects_trailing_tilde_in_token() -> None:
    with pytest.raises(InvalidPointerError):
        parse("/foo~")


def test_format_pointer_empty_yields_empty_string() -> None:
    assert format_pointer([]) == ""


def test_format_pointer_rejects_non_string_token() -> None:
    with pytest.raises(TypeError):
        format_pointer(["ok", 5])  # type: ignore[list-item]


def test_format_pointer_accepts_iterators() -> None:
    assert format_pointer(iter(["foo", "bar"])) == "/foo/bar"


def test_to_pointer_matches_format_pointer() -> None:
    assert to_pointer() == ""
    assert to_pointer("foo", "bar") == "/foo/bar"
    assert to_pointer("a/b", "c~d") == "/a~1b/c~0d"


def test_parse_examples_from_rfc_6901() -> None:
    expected = {
        "": (),
        "/foo": ("foo",),
        "/foo/0": ("foo", "0"),
        "/": ("",),
        "/a~1b": ("a/b",),
        "/c%d": ("c%d",),
        "/e^f": ("e^f",),
        "/g|h": ("g|h",),
        "/i\\j": ("i\\j",),
        '/k"l': ('k"l',),
        "/ ": (" ",),
        "/m~0n": ("m~n",),
    }
    for pointer, tokens in expected.items():
        assert parse(pointer) == tokens
        assert format_pointer(tokens) == pointer
