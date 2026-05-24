"""set_value / remove — in-place document mutation."""

from __future__ import annotations

from typing import Any

import pytest

from jsonptr import ResolutionError, remove, set_value

# ---------------------------------------------------------------------------
# set_value
# ---------------------------------------------------------------------------


def test_set_value_replaces_existing_dict_key() -> None:
    doc: dict[str, Any] = {"foo": 1, "bar": 2}
    set_value(doc, "/foo", 42)
    assert doc == {"foo": 42, "bar": 2}


def test_set_value_creates_new_dict_key() -> None:
    doc: dict[str, Any] = {}
    set_value(doc, "/x", "value")
    assert doc == {"x": "value"}


def test_set_value_replaces_existing_list_index() -> None:
    doc: list[Any] = ["a", "b", "c"]
    set_value(doc, "/1", "B")
    assert doc == ["a", "B", "c"]


def test_set_value_appends_at_end_of_array_marker() -> None:
    doc: list[Any] = ["a", "b"]
    set_value(doc, "/-", "c")
    assert doc == ["a", "b", "c"]


def test_set_value_append_via_one_past_end_index() -> None:
    doc: list[Any] = ["a", "b"]
    set_value(doc, "/2", "c")
    assert doc == ["a", "b", "c"]


def test_set_value_rejects_root_pointer() -> None:
    doc: dict[str, Any] = {"x": 1}
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "", "anything")
    assert "root" in info.value.detail


def test_set_value_rejects_out_of_range_list_index() -> None:
    doc: list[Any] = ["a", "b"]
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "/5", "x")
    assert "out of range" in info.value.detail


def test_set_value_rejects_invalid_list_index() -> None:
    doc: list[Any] = ["a"]
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "/01", "x")
    assert "invalid array index" in info.value.detail


def test_set_value_rejects_missing_intermediate_dict_key() -> None:
    doc: dict[str, Any] = {}
    with pytest.raises(ResolutionError):
        set_value(doc, "/a/b", 1)


def test_set_value_rejects_scalar_terminal_parent() -> None:
    # Two-token path: walk lands on a scalar, assign fails.
    doc: dict[str, Any] = {"a": 1}
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "/a/b", "x")
    assert "cannot assign" in info.value.detail


def test_set_value_rejects_scalar_intermediate_parent() -> None:
    # Three-token path: walk must step *through* a scalar, failing.
    doc: dict[str, Any] = {"a": 1}
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "/a/b/c", "x")
    assert "cannot traverse" in info.value.detail


def test_set_value_nested_path() -> None:
    doc: dict[str, Any] = {"a": {"b": {"c": 1}}}
    set_value(doc, "/a/b/c", 99)
    assert doc["a"]["b"]["c"] == 99


def test_set_value_handles_escaped_token() -> None:
    doc: dict[str, Any] = {}
    set_value(doc, "/a~1b", "slash")
    set_value(doc, "/m~0n", "tilde")
    assert doc == {"a/b": "slash", "m~n": "tilde"}


def test_set_value_into_nested_list_element() -> None:
    doc: dict[str, Any] = {"rows": [{"x": 1}, {"x": 2}]}
    set_value(doc, "/rows/1/x", 22)
    assert doc["rows"][1]["x"] == 22


def test_set_value_into_set_unsupported_container() -> None:
    # Sets are not allowed as containers.
    doc: dict[str, Any] = {"s": {1, 2, 3}}
    with pytest.raises(ResolutionError) as info:
        set_value(doc, "/s/0", "x")
    assert "cannot assign" in info.value.detail


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove_dict_key_returns_value() -> None:
    doc: dict[str, Any] = {"a": 1, "b": 2}
    out = remove(doc, "/a")
    assert out == 1
    assert doc == {"b": 2}


def test_remove_list_index_returns_value() -> None:
    doc: list[Any] = ["x", "y", "z"]
    out = remove(doc, "/1")
    assert out == "y"
    assert doc == ["x", "z"]


def test_remove_missing_dict_key_raises() -> None:
    doc: dict[str, Any] = {"a": 1}
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/missing")
    assert "key not found" in info.value.detail


def test_remove_out_of_range_list_index_raises() -> None:
    doc: list[Any] = ["a"]
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/5")
    assert "out of range" in info.value.detail


def test_remove_invalid_list_index_raises() -> None:
    doc: list[Any] = ["a"]
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/01")
    assert "invalid array index" in info.value.detail


def test_remove_rejects_end_of_array_marker() -> None:
    doc: list[Any] = ["a", "b"]
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/-")
    assert "not a removable" in info.value.detail


def test_remove_rejects_root_pointer() -> None:
    doc: dict[str, Any] = {"x": 1}
    with pytest.raises(ResolutionError) as info:
        remove(doc, "")
    assert "root" in info.value.detail


def test_remove_rejects_scalar_terminal_parent() -> None:
    doc: dict[str, Any] = {"a": 1}
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/a/b")
    assert "cannot remove" in info.value.detail


def test_remove_rejects_scalar_intermediate_parent() -> None:
    doc: dict[str, Any] = {"a": 1}
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/a/b/c")
    assert "cannot traverse" in info.value.detail


def test_remove_nested_path() -> None:
    doc: dict[str, Any] = {"a": {"b": {"c": 99}}}
    out = remove(doc, "/a/b/c")
    assert out == 99
    assert doc == {"a": {"b": {}}}


def test_remove_unsupported_container() -> None:
    doc: dict[str, Any] = {"s": (1, 2, 3)}
    with pytest.raises(ResolutionError) as info:
        remove(doc, "/s/0")
    assert "cannot remove" in info.value.detail
