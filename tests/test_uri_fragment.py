"""URI-fragment representation from RFC 6901 §6."""

from __future__ import annotations

import pytest

from jsonptr import (
    InvalidPointerError,
    format_pointer,
    format_uri_fragment,
    parse_uri_fragment,
    resolve,
)


@pytest.mark.parametrize(
    "fragment,tokens",
    [
        ("#", ()),
        ("#/foo", ("foo",)),
        ("#/foo/0", ("foo", "0")),
        ("#/", ("",)),
        ("#/a~1b", ("a/b",)),
        ("#/c%25d", ("c%d",)),
        ("#/e%5Ef", ("e^f",)),
        ("#/g%7Ch", ("g|h",)),
        ("#/i%5Cj", ("i\\j",)),
        ("#/k%22l", ('k"l',)),
        ("#/%20", (" ",)),
        ("#/m~0n", ("m~n",)),
        ("#/%E2%98%83", ("\u2603",)),
    ],
)
def test_parse_uri_fragment_examples(fragment: str, tokens: tuple[str, ...]) -> None:
    assert parse_uri_fragment(fragment) == tokens


@pytest.mark.parametrize(
    "tokens,fragment",
    [
        ((), "#"),
        (("foo", "0"), "#/foo/0"),
        (("a/b",), "#/a~1b"),
        (("c%d",), "#/c%25d"),
        (("e^f",), "#/e%5Ef"),
        (("g|h",), "#/g%7Ch"),
        (("i\\j",), "#/i%5Cj"),
        (('k"l',), "#/k%22l"),
        ((" ",), "#/%20"),
        (("m~n",), "#/m~0n"),
        (("\u2603",), "#/%E2%98%83"),
        (("query?ok",), "#/query?ok"),
    ],
)
def test_format_uri_fragment_examples(tokens: tuple[str, ...], fragment: str) -> None:
    assert format_uri_fragment(tokens) == fragment
    assert parse_uri_fragment(fragment) == tokens


def test_uri_fragment_tokens_resolve_against_document() -> None:
    document = {"foo": ["bar"], "c%d": 2, "snow": {"\u2603": "cold"}}
    foo_pointer = format_pointer(parse_uri_fragment(format_uri_fragment(("foo", "0"))))
    percent_pointer = format_pointer(parse_uri_fragment(format_uri_fragment(("c%d",))))
    snow_pointer = format_pointer(
        parse_uri_fragment(format_uri_fragment(("snow", "\u2603")))
    )

    assert resolve(document, foo_pointer) == "bar"
    assert resolve(document, percent_pointer) == 2
    assert resolve(document, snow_pointer) == "cold"


def test_parse_uri_fragment_requires_hash_prefix() -> None:
    with pytest.raises(InvalidPointerError, match="must begin with '#'"):
        parse_uri_fragment("/foo")


@pytest.mark.parametrize("fragment", ["#/%", "#/%0", "#/%GG"])
def test_parse_uri_fragment_rejects_bad_percent_escape(fragment: str) -> None:
    with pytest.raises(InvalidPointerError, match="invalid percent escape"):
        parse_uri_fragment(fragment)


def test_parse_uri_fragment_rejects_invalid_utf8() -> None:
    with pytest.raises(InvalidPointerError, match="not valid UTF-8"):
        parse_uri_fragment("#/%FF")


def test_parse_uri_fragment_rejects_decoded_non_pointer() -> None:
    with pytest.raises(InvalidPointerError, match="decoded fragment"):
        parse_uri_fragment("#foo")


def test_uri_fragment_type_errors_are_explicit() -> None:
    with pytest.raises(TypeError):
        parse_uri_fragment(7)  # type: ignore[arg-type]
