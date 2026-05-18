"""End-to-end scenarios that mix every public entry point."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from jsonptr import (
    get,
    has,
    parse,
    remove,
    resolve,
    set_value,
    to_pointer,
)


@pytest.fixture()
def order() -> dict[str, Any]:
    return {
        "id": "ord-42",
        "customer": {"name": "Ada", "addresses": []},
        "items": [
            {"sku": "S-1", "qty": 2, "price": 9.99},
            {"sku": "S-2", "qty": 1, "price": 19.5},
        ],
        "tags": ["urgent", "gift"],
        "meta": {"source/channel": "web", "campaign~id": "spring"},
    }


def test_round_trip_parse_format_via_to_pointer(
    order: dict[str, Any],
) -> None:
    tokens = parse("/meta/source~1channel")
    pointer = to_pointer(*tokens)
    assert pointer == "/meta/source~1channel"
    assert resolve(order, pointer) == "web"


def test_full_lifecycle_on_a_record(order: dict[str, Any]) -> None:
    pointer = to_pointer("items", "-")
    set_value(order, pointer, {"sku": "S-3", "qty": 1, "price": 4.5})
    assert len(order["items"]) == 3
    assert resolve(order, "/items/2/sku") == "S-3"

    removed = remove(order, "/items/0")
    assert removed["sku"] == "S-1"
    assert resolve(order, "/items/0/sku") == "S-2"

    set_value(order, "/customer/addresses/-", {"city": "Stockholm"})
    assert resolve(order, "/customer/addresses/0/city") == "Stockholm"

    assert has(order, "/customer/addresses/0/city")
    assert not has(order, "/customer/addresses/0/zip")
    assert get(order, "/customer/addresses/0/zip", default="") == ""


def test_immutable_walk_does_not_mutate_input(
    order: dict[str, Any],
) -> None:
    snapshot = copy.deepcopy(order)
    for pointer in ("", "/items/0/sku", "/meta/campaign~0id"):
        resolve(order, pointer)
        get(order, pointer, default=None)
        has(order, pointer)
    assert order == snapshot


def test_escaped_metadata_keys_round_trip(
    order: dict[str, Any],
) -> None:
    src = "/meta/source~1channel"
    cam = "/meta/campaign~0id"
    assert resolve(order, src) == "web"
    assert resolve(order, cam) == "spring"

    set_value(order, src, "mobile")
    set_value(order, cam, "summer")
    assert resolve(order, src) == "mobile"
    assert resolve(order, cam) == "summer"


def test_resolve_followed_by_remove_pair(order: dict[str, Any]) -> None:
    pointer = "/tags/0"
    value = resolve(order, pointer)
    assert value == "urgent"
    removed = remove(order, pointer)
    assert removed == "urgent"
    assert order["tags"] == ["gift"]
