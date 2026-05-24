"""jsonptr — RFC 6901 JSON Pointer for Python.

A zero-dependency, fully-typed implementation of JSON Pointer
(RFC 6901). Resolves, inspects, and mutates nested ``dict`` / ``list``
structures using a compact pointer syntax::

    /foo/0/bar    →  document["foo"][0]["bar"]
    ""            →  the document itself
    /             →  document[""]   (key is the empty string)
    /a~1b         →  document["a/b"]
    /a~0b         →  document["a~b"]

Public surface:

* :func:`parse`, :func:`format_pointer` — string ↔ token tuple.
* :func:`parse_uri_fragment`, :func:`format_uri_fragment` — RFC 6901
  URI-fragment form.
* :func:`escape`, :func:`unescape` — single-token transforms.
* :func:`resolve`, :func:`get`, :func:`has` — read access.
* :func:`set_value`, :func:`remove` — in-place mutation.
* :func:`to_pointer` — convenience constructor.
* Errors: :class:`JsonPointerError` ⊃ :class:`InvalidPointerError`,
  :class:`ResolutionError`.
"""

from __future__ import annotations

from ._errors import (
    InvalidPointerError,
    JsonPointerError,
    ResolutionError,
)
from ._index import END_OF_ARRAY
from ._parse import (
    escape,
    format_pointer,
    format_uri_fragment,
    parse,
    parse_uri_fragment,
    unescape,
)
from ._resolve import get, has, remove, resolve, set_value, to_pointer

__all__ = [
    "END_OF_ARRAY",
    "InvalidPointerError",
    "JsonPointerError",
    "ResolutionError",
    "escape",
    "format_pointer",
    "format_uri_fragment",
    "get",
    "has",
    "parse",
    "parse_uri_fragment",
    "remove",
    "resolve",
    "set_value",
    "to_pointer",
    "unescape",
]
__version__ = "0.1.0"
