"""Error hierarchy for :mod:`jsonptr`.

All errors inherit from :class:`JsonPointerError`, which itself is a
:class:`ValueError`. This lets callers either catch the broad family
or pick out the specific subclass.
"""

from __future__ import annotations

from typing import Optional


class JsonPointerError(ValueError):
    """Base class for every :mod:`jsonptr` failure."""


class InvalidPointerError(JsonPointerError):
    """Raised when a pointer string is syntactically malformed.

    A JSON Pointer is malformed when it is non-empty and does not
    start with ``/``, or when an escape sequence in a token is
    incomplete (``~`` not followed by ``0`` or ``1``).
    """

    def __init__(self, pointer: str, detail: str) -> None:
        self.pointer = pointer
        self.detail = detail
        super().__init__(f"invalid JSON pointer {pointer!r}: {detail}")


class ResolutionError(JsonPointerError):
    """Raised when a pointer cannot be resolved against a document.

    Attributes
    ----------
    pointer:
        The full original pointer string.
    path:
        The tuple of tokens that were successfully traversed before
        the failure.
    token:
        The token that could not be resolved, or ``None`` if the
        failure was at the root (e.g. wrong default-handling state).
    detail:
        Human-readable description of the failure mode.
    """

    def __init__(
        self,
        pointer: str,
        path: tuple[str, ...],
        token: Optional[str],
        detail: str,
    ) -> None:
        self.pointer = pointer
        self.path = path
        self.token = token
        self.detail = detail
        super().__init__(
            f"cannot resolve {pointer!r} at "
            f"{format_path(path)!r}: {detail}"
        )


def format_path(path: tuple[str, ...]) -> str:
    """Format a token tuple back into a pointer string for messages."""

    if not path:
        return ""
    parts = []
    for token in path:
        parts.append(token.replace("~", "~0").replace("/", "~1"))
    return "/" + "/".join(parts)
