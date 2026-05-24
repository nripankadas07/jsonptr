"""Resolve / get / has — read-only document traversal."""

from __future__ import annotations

from typing import Any

import pytest

from jsonptr import (
    InvalidPointerError,
    ResolutionError,
    get,
    has,
    resolve,
)


# The canonical document from RFC 6901 §5.
@pytest.fixture()
def doc() -> dict[str, Any]:
    return {
        "foo": ["bar", "baz"],
        "": 0,
        "a/b": 1,
        "c%d": 2,
        "e^f": 3,
        "g|h": 4,
        "i\\j": 5,
        'k"l': 6,
        " ": 7,
        "m~n": 8,
        "nested": {"x": {"y": [10, 20, {"z": "deep"}]}},
    }


def test_root_pointer_returns_document(doc: dict[str, Any]) -> None:
    assert resolve(doc, "") is doc


def test_simple_key_lookup(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/foo") == ["bar", "baz"]


def test_array_index_lookup(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/foo/0") == "bar"
    assert resolve(doc, "/foo/1") == "baz"


def test_empty_string_key(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/") == 0


def test_escaped_slash_key(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/a~1b") == 1


def test_escaped_tilde_key(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/m~0n") == 8


@pytest.mark.parametrize(
    "pointer,expected",
    [
        ("/c%d", 2),
        ("/e^f", 3),
        ("/g|h", 4),
        ("/i\\j", 5),
        ('/k"l', 6),
        ("/ ", 7),
    ],
)
def test_rfc_examples(doc: dict[str, Any], pointer: str, expected: int) -> None:
    assert resolve(doc, pointer) == expected


def test_deep_nested_traversal(doc: dict[str, Any]) -> None:
    assert resolve(doc, "/nested/x/y/0") == 10
    assert resolve(doc, "/nested/x/y/2/z") == "deep"


def test_resolve_unknown_key_raises(doc: dict[str, Any]) -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(doc, "/missing")
    assert info.value.token == "missing"
    assert info.value.path == ()


def test_resolve_index_out_of_range_raises(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(doc, "/foo/7")
    assert info.value.token == "7"
    assert info.value.path == ("foo",)
    assert "out of range" in info.value.detail


def test_resolve_invalid_array_index_raises(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(doc, "/foo/01")
    assert info.value.detail == "invalid array index"


def test_resolve_end_of_array_marker_unreadable(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(doc, "/foo/-")
    assert "not a readable" in info.value.detail


def test_resolve_traverse_scalar_raises(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(doc, "/foo/0/extra")
    assert "cannot traverse" in info.value.detail


def test_resolve_invalid_pointer_propagates(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(InvalidPointerError):
        resolve(doc, "no/leading/slash")


def test_get_returns_default_on_missing(
    doc: dict[str, Any],
) -> None:
    assert get(doc, "/missing", default="fallback") == "fallback"
    assert get(doc, "/foo/9", default=None) is None


def test_get_raises_when_no_default(doc: dict[str, Any]) -> None:
    with pytest.raises(ResolutionError):
        get(doc, "/missing")


def test_get_returns_actual_value_when_present(
    doc: dict[str, Any],
) -> None:
    assert get(doc, "/foo/0", default="never") == "bar"


def test_get_default_does_not_swallow_invalid_pointer(
    doc: dict[str, Any],
) -> None:
    with pytest.raises(InvalidPointerError):
        get(doc, "not-a-pointer", default="x")


def test_has_true_on_existing(doc: dict[str, Any]) -> None:
    assert has(doc, "/foo/0") is True
    assert has(doc, "") is True
    assert has(doc, "/") is True


def test_has_false_on_missing(doc: dict[str, Any]) -> None:
    assert has(doc, "/missing") is False
    assert has(doc, "/foo/99") is False
    assert has(doc, "/foo/-") is False


def test_has_propagates_invalid_pointer(doc: dict[str, Any]) -> None:
    with pytest.raises(InvalidPointerError):
        has(doc, "no-slash")


def test_resolve_traverse_list_with_key_token() -> None:
    with pytest.raises(ResolutionError) as info:
        resolve(["a", "b"], "/key")
    assert info.value.detail == "invalid array index"


def test_resolve_traverse_dict_with_index_token() -> None:
    # Treating "0" as a dict key works fine when the dict has it.
    assert resolve({"0": "zero"}, "/0") == "zero"


def test_resolve_traverse_dict_with_missing_index_token() -> None:
    with pytest.raises(ResolutionError):
        resolve({"a": 1}, "/0")
