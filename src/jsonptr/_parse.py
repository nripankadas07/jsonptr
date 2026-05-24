"""Pointer string ↔ token-tuple conversion (RFC 6901 §3, §4)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final
from urllib.parse import quote, unquote_to_bytes

from ._errors import InvalidPointerError

_FRAGMENT_SAFE: Final[str] = "/?:@!$&'()*+,;=~"
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdefABCDEF")


def escape(token: str) -> str:
    """Escape a single reference token per RFC 6901 §3.

    The escape order matters: ``~`` must be replaced *before* ``/``
    so that an existing ``/`` does not get further mangled.
    """

    if not isinstance(token, str):
        raise TypeError(f"escape() expects a str, got {type(token).__name__}")
    return token.replace("~", "~0").replace("/", "~1")


def unescape(token: str) -> str:
    """Unescape a single reference token per RFC 6901 §4.

    The reverse-of-escape order matters: ``~1`` is replaced first,
    then ``~0``. A bare ``~`` not followed by ``0`` or ``1`` is a
    syntax error.
    """

    if not isinstance(token, str):
        raise TypeError(f"unescape() expects a str, got {type(token).__name__}")
    _validate_escape_sequences(token)
    return token.replace("~1", "/").replace("~0", "~")


def _validate_escape_sequences(token: str) -> None:
    index = 0
    while index < len(token):
        char = token[index]
        if char == "~":
            if index + 1 >= len(token):
                raise InvalidPointerError(token, "dangling '~' at end of token")
            nxt = token[index + 1]
            if nxt not in ("0", "1"):
                raise InvalidPointerError(
                    token,
                    f"'~' must be followed by '0' or '1', got {nxt!r}",
                )
            index += 2
            continue
        index += 1


def parse(pointer: str) -> tuple[str, ...]:
    """Parse a JSON Pointer string into its sequence of tokens.

    An empty string returns an empty tuple — the pointer to the
    root document. Otherwise the pointer must begin with ``/``.
    """

    if not isinstance(pointer, str):
        raise TypeError(f"parse() expects a str, got {type(pointer).__name__}")
    if pointer == "":
        return ()
    if not pointer.startswith("/"):
        raise InvalidPointerError(
            pointer,
            "non-empty pointer must begin with '/'",
        )
    raw_tokens = pointer.split("/")[1:]
    return tuple(unescape(token) for token in raw_tokens)


def format_pointer(tokens: Iterable[str]) -> str:
    """Format a sequence of tokens back into a pointer string.

    The inverse of :func:`parse`. ``format_pointer([])`` returns the
    empty string (root pointer); each token is RFC-6901 escaped.
    """

    if isinstance(tokens, str):
        raise TypeError("format_pointer() expects an iterable of tokens, not str")
    materialised = list(tokens)
    if not materialised:
        return ""
    parts = []
    for token in materialised:
        if not isinstance(token, str):
            raise TypeError(
                f"format_pointer() tokens must all be str, got {type(token).__name__}"
            )
        parts.append(escape(token))
    return "/" + "/".join(parts)


def parse_uri_fragment(fragment: str) -> tuple[str, ...]:
    """Parse the URI-fragment form from RFC 6901 §6.

    ``#`` is the root pointer, ``#/foo/0`` is equivalent to
    ``/foo/0``, and percent-encoded octets are decoded as UTF-8
    before normal JSON Pointer parsing is applied.
    """

    if not isinstance(fragment, str):
        raise TypeError(
            f"parse_uri_fragment() expects a str, got {type(fragment).__name__}"
        )
    if not fragment.startswith("#"):
        raise InvalidPointerError(fragment, "URI fragment must begin with '#'")
    encoded = fragment[1:]
    _validate_percent_escapes(encoded, fragment)
    try:
        pointer = unquote_to_bytes(encoded).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidPointerError(
            fragment,
            f"URI fragment is not valid UTF-8: {exc.reason}",
        ) from exc
    try:
        return parse(pointer)
    except InvalidPointerError as exc:
        raise InvalidPointerError(
            fragment,
            f"decoded fragment is not a valid JSON Pointer: {exc.detail}",
        ) from exc


def _validate_percent_escapes(encoded: str, original: str) -> None:
    index = 0
    while index < len(encoded):
        if encoded[index] != "%":
            index += 1
            continue
        if (
            index + 2 >= len(encoded)
            or encoded[index + 1] not in _HEX_DIGITS
            or encoded[index + 2] not in _HEX_DIGITS
        ):
            raise InvalidPointerError(
                original,
                f"invalid percent escape at fragment offset {index + 1}",
            )
        index += 3


def format_uri_fragment(tokens: Iterable[str]) -> str:
    """Format tokens as the RFC 6901 URI-fragment representation."""

    pointer = format_pointer(tokens)
    return "#" + quote(pointer, safe=_FRAGMENT_SAFE)
