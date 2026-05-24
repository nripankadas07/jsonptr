# Contributing

Thanks for considering a contribution to `jsonptr`. Keep changes
small, tested, and aligned with the existing public API. This library
is tiny on purpose; the hard part is preserving exact edge-case
behavior, not adding surface area casually.

## Local checks

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest --cov=jsonptr --cov-branch --cov-fail-under=100
mypy --strict src/jsonptr
python -m build
```

## Contribution rules

- Add or update tests for behavior changes.
- Keep branch coverage at 100%; parser error branches need explicit
  tests.
- Keep README examples in sync with the implementation.
- Keep runtime dependencies at zero unless there is an exceptional
  reason.
- Prefer explicit errors over surprising coercions.
- Preserve the distinction between RFC 6901 resolution and mutation
  helpers: `-` is not a readable array index.
