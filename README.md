# jsonptr

A small, strict, zero-dependency [RFC 6901](https://datatracker.ietf.org/doc/html/rfc6901)
JSON Pointer for Python. Parse pointer strings, resolve them against nested
`dict` / `list` documents, and mutate the targets in place — all with
descriptive errors and a fully typed surface.

```text
/foo/0/bar    →  document["foo"][0]["bar"]
""            →  the document itself
/             →  document[""]   (key is the empty string)
/a~1b         →  document["a/b"]
/a~0b         →  document["a~b"]
```

## Install

```bash
python -m pip install -e .
```

The package has zero runtime dependencies and supports Python 3.9+.

## Quick start

```python
import jsonptr

doc = {
    "foo": ["bar", "baz"],
    "meta": {"source/channel": "web", "campaign~id": "spring"},
}

jsonptr.resolve(doc, "/foo/0")               # → "bar"
jsonptr.resolve(doc, "/meta/source~1channel") # → "web"
jsonptr.get(doc, "/missing", default=None)    # → None
jsonptr.parse_uri_fragment("#/meta/campaign~0id") # → ("meta", "campaign~id")

jsonptr.set_value(doc, "/foo/-", "qux")       # append to array
jsonptr.set_value(doc, "/meta/campaign~0id", "summer")

jsonptr.remove(doc, "/foo/0")                  # → "bar"
jsonptr.has(doc, "/foo/0")                     # → True
```

## Standards notes

`jsonptr` covers both JSON Pointer string form from RFC 6901 sections
3-5 and URI-fragment form from section 6. Fragment helpers require the
leading `#`, validate percent escapes, decode UTF-8 strictly, and then
apply normal JSON Pointer parsing.

The `-` array token is deliberately split by operation. Resolution
treats it as an error, matching RFC 6901's "one past the end" behavior.
`set_value(..., "/-", value)` accepts it as a final token for
JSON Patch-style appends; `remove(..., "/-")` still rejects it.

Reference: [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901.html).

## API reference

### Pointer strings

`parse(pointer) -> tuple[str, ...]` — Parse a pointer string into the
sequence of unescaped reference tokens. Empty string yields the empty
tuple (the root pointer). Raises `InvalidPointerError` for malformed
input.

`format_pointer(tokens) -> str` — The inverse of `parse`. Each token is
RFC-6901 escaped.

`to_pointer(*tokens) -> str` — Convenience wrapper around
`format_pointer` that takes positional arguments.

`parse_uri_fragment(fragment) -> tuple[str, ...]` — Parse the URI
fragment representation, for example `#/foo/0` or `#/c%25d`. Raises
`InvalidPointerError` for a missing `#`, invalid percent escape,
invalid UTF-8, or decoded non-pointer.

`format_uri_fragment(tokens) -> str` — Format tokens as a URI
fragment. The root pointer becomes `#`; characters outside the URI
fragment grammar are percent-encoded as UTF-8.

`escape(token) -> str` — Escape a single token: `~` → `~0`, `/` → `~1`,
in that order.

`unescape(token) -> str` — The inverse of `escape`. Raises
`InvalidPointerError` on a dangling `~` or an unknown `~X` sequence.

### Resolution

`resolve(document, pointer) -> Any` — Walk `pointer` through `document`
and return the value. Raises `InvalidPointerError` for malformed
pointers, `ResolutionError` for missing keys / out-of-range indices /
non-container traversals.

`get(document, pointer, *, default=...) -> Any` — Like `resolve` but
returns `default` on `ResolutionError`. Malformed pointers still raise.

`has(document, pointer) -> bool` — Non-raising existence check (for
resolution failures). Malformed pointers still raise.

### Mutation

`set_value(document, pointer, value) -> None` — Set `value` at the
target in place. The final token may be `-` for arrays (appends) or
the index equal to the array's length (also appends). Intermediate
containers must already exist.

`remove(document, pointer) -> Any` — Remove and return the value at
the target. The root pointer (`""`) and the `-` marker are not valid
removal targets.

### Errors

```python
JsonPointerError(ValueError)
├── InvalidPointerError   # syntactic problem with the pointer string
└── ResolutionError       # could not resolve / mutate inside the doc
    .pointer  # full pointer string
    .path     # tokens successfully traversed
    .token    # the failing token (or None for root)
    .detail   # human-readable description
```

### Constants

`END_OF_ARRAY = "-"` — The token for the position past the end of an
array. It is not readable or removable; `set_value` accepts it only as
the final token to append.

## Running tests

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest --cov=jsonptr --cov-branch --cov-report=term-missing --cov-fail-under=100
mypy --strict src/jsonptr
python -m build
```

The full suite is 156 tests across eight modules with **100% line and
100% branch coverage**; `mypy --strict` passes across all five source
files.

## License

MIT — see [LICENSE](./LICENSE).
