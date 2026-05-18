"""Tests for the array-index token helpers."""

from __future__ import annotations

import pytest

from jsonptr._index import (
    END_OF_ARRAY,
    is_end_of_array,
    parse_array_index,
)


@pytest.mark.parametrize(
    "token,expected",
    [
        ("0", 0),
        ("1", 1),
        ("9", 9),
        ("10", 10),
        ("123", 123),
        ("999999", 999999),
    ],
)
def test_parse_array_index_accepts_canonical_digits(
    token: str, expected: int
) -> None:
    assert parse_array_index(token) == expected


@pytest.mark.parametrize(
    "token",
    [
        "",
        "01",
        "007",
        "-1",
        "+1",
        " 1",
        "1 ",
        "1.0",
        "1e2",
        "abc",
        "0xff",
        "1_000",
    ],
)
def test_parse_array_index_rejects_invalid(token: str) -> None:
    assert parse_array_index(token) is None


def test_is_end_of_array() -> None:
    assert is_end_of_array("-")
    assert not is_end_of_array("0")
    assert not is_end_of_array("--")
    assert not is_end_of_array("")


def test_end_of_array_constant_value() -> None:
    assert END_OF_ARRAY == "-"
