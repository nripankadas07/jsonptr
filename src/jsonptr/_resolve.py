"""Document traversal: get / has / set / remove (RFC 6901 §5)."""

from __future__ import annotations

from typing import Any

from ._errors import ResolutionError
from ._index import is_end_of_array, parse_array_index
from ._parse import format_pointer, parse

_MISSING = object()


def _fail(
    pointer: str,
    path: tuple[str, ...],
    token: str,
    detail: str,
) -> ResolutionError:
    return ResolutionError(pointer, path, token, detail)


def _check_list_index(
    container: list[Any],
    token: str,
    *,
    pointer: str,
    path: tuple[str, ...],
    allow_append: bool = False,
) -> int:
    index = parse_array_index(token)
    if index is None:
        raise _fail(pointer, path, token, "invalid array index")
    limit = len(container) if not allow_append else len(container) + 1
    if index >= limit:
        raise _fail(
            pointer,
            path,
            token,
            f"index {index} out of range (length {len(container)})",
        )
    return index


def _step_list(
    container: list[Any],
    token: str,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> Any:
    if is_end_of_array(token):
        raise _fail(pointer, path, token, "'-' is not a readable index")
    index = _check_list_index(container, token, pointer=pointer, path=path)
    return container[index]


def _step(
    container: Any,
    token: str,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> Any:
    """Descend one token; raise :class:`ResolutionError` on failure."""

    if isinstance(container, list):
        return _step_list(container, token, pointer=pointer, path=path)
    if isinstance(container, dict):
        if token not in container:
            raise _fail(pointer, path, token, "key not found in object")
        return container[token]
    raise _fail(pointer, path, token, f"cannot traverse {type(container).__name__}")


def resolve(document: Any, pointer: str) -> Any:
    """Return the value pointed to by ``pointer`` inside ``document``.

    Raises :class:`InvalidPointerError` if the pointer is malformed
    and :class:`ResolutionError` if it cannot be resolved.
    """

    tokens = parse(pointer)
    return _walk_for_get(document, tokens, pointer)


def _walk_for_get(document: Any, tokens: tuple[str, ...], pointer: str) -> Any:
    current: Any = document
    walked: list[str] = []
    for token in tokens:
        current = _step(current, token, pointer=pointer, path=tuple(walked))
        walked.append(token)
    return current


def get(document: Any, pointer: str, *, default: Any = _MISSING) -> Any:
    """Like :func:`resolve` but returns ``default`` on failure.

    If ``default`` is left unset, behaves identically to
    :func:`resolve` (raises on missing/invalid path).
    """

    try:
        return resolve(document, pointer)
    except ResolutionError:
        if default is _MISSING:
            raise
        return default


def has(document: Any, pointer: str) -> bool:
    """Return ``True`` iff ``pointer`` resolves inside ``document``.

    Malformed pointers still raise :class:`InvalidPointerError` —
    only resolution failures are converted to ``False``.
    """

    try:
        resolve(document, pointer)
    except ResolutionError:
        return False
    return True


def _assign_list(
    parent: list[Any],
    token: str,
    value: Any,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> None:
    if is_end_of_array(token):
        parent.append(value)
        return
    index = _check_list_index(
        parent, token, pointer=pointer, path=path, allow_append=True
    )
    if index == len(parent):
        parent.append(value)
    else:
        parent[index] = value


def _assign(
    parent: Any,
    token: str,
    value: Any,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> None:
    if isinstance(parent, list):
        _assign_list(parent, token, value, pointer=pointer, path=path)
        return
    if isinstance(parent, dict):
        parent[token] = value
        return
    raise _fail(
        pointer,
        path,
        token,
        f"cannot assign into {type(parent).__name__}",
    )


def set_value(
    document: dict[str, Any] | list[Any],
    pointer: str,
    value: Any,
) -> None:
    """Set ``value`` at ``pointer`` inside ``document`` in place.

    For lists, the final token may be the ``-`` marker or the index
    equal to the list length, in which case ``value`` is appended.
    Otherwise the final token must address an existing position; this
    function does NOT auto-create intermediate containers.
    """

    tokens = parse(pointer)
    if not tokens:
        raise _fail(pointer, (), "", "cannot set the root document")
    parent = _walk_for_get(document, tokens[:-1], pointer)
    final = tokens[-1]
    _assign(parent, final, value, pointer=pointer, path=tokens[:-1])


def _pop_list(
    parent: list[Any],
    token: str,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> Any:
    if is_end_of_array(token):
        raise _fail(pointer, path, token, "'-' is not a removable index")
    index = _check_list_index(parent, token, pointer=pointer, path=path)
    return parent.pop(index)


def _pop(
    parent: Any,
    token: str,
    *,
    pointer: str,
    path: tuple[str, ...],
) -> Any:
    if isinstance(parent, list):
        return _pop_list(parent, token, pointer=pointer, path=path)
    if isinstance(parent, dict):
        if token not in parent:
            raise _fail(pointer, path, token, "key not found in object")
        return parent.pop(token)
    raise _fail(pointer, path, token, f"cannot remove from {type(parent).__name__}")


def remove(document: dict[str, Any] | list[Any], pointer: str) -> Any:
    """Remove the value at ``pointer`` and return it.

    The root document cannot be removed (raises
    :class:`ResolutionError`). For lists, the ``-`` marker is not a
    valid target (you cannot remove "one past the end").
    """

    tokens = parse(pointer)
    if not tokens:
        raise _fail(pointer, (), "", "cannot remove the root document")
    parent = _walk_for_get(document, tokens[:-1], pointer)
    final = tokens[-1]
    return _pop(parent, final, pointer=pointer, path=tokens[:-1])


def to_pointer(*tokens: str) -> str:
    """Convenience: build a pointer from raw (unescaped) tokens.

    Equivalent to :func:`format_pointer` but takes positional args,
    which is friendlier for code that constructs pointers inline.
    """

    return format_pointer(tokens)
