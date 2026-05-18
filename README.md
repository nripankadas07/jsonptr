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
pip install jsonptr
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

jsonptr.set_value(doc, "/foo/-", "qux")       # append to array
jsonptr.set_value(doc, "/meta/campaign~0id", "summer")

jsonptr.remove(doc, "/foo/0")                  # → "bar"
jsonptr.has(doc, "/foo/0")                     # → True
```

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

`END_OF_ARRAY = "-"` — The RFC-6901 marker for the position past the
end of an array; valid as the final token of a `set_value` call.

## Running tests

```bash
pip install pytest pytest-cov mypy
pytest --cov=jsonptr --cov-branch --cov-report=term-missing
mypy --strict src/jsonptr
```

The full suite is 122 tests across six modules with **100% line and
100% branch coverage**; `mypy --strict` passes across all five source
files.

## License

MIT — see [LICENSE](./LICENSE).
