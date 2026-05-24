"""Helpers for interpreting array index tokens (RFC 6901 §4)."""

from __future__ import annotations

END_OF_ARRAY = "-"


def parse_array_index(token: str) -> int | None:
    """Return the integer index represented by ``token`` or ``None``.

    Returns ``None`` if the token cannot be a valid array index.
    Per RFC 6901 §4, the index token must be either ``0`` or a
    non-empty string of digits with no leading zero. The ``-`` token
    denotes the "one past the end" position and is intentionally not
    handled here; call sites must decide whether that operation can
    use it.
    """

    if token == "":
        return None
    if token == "0":
        return 0
    if token[0] == "0":
        return None
    for char in token:
        if not ("0" <= char <= "9"):
            return None
    return int(token)


def is_end_of_array(token: str) -> bool:
    """Return ``True`` iff ``token`` is the special end-of-array marker."""

    return token == END_OF_ARRAY
