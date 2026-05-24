# jsonptr quality bar

This repository is part of a public portfolio, so the bar is practical
correctness, clear documentation, and reproducible checks. For
`jsonptr`, "quality" means exact RFC 6901 escaping, URI-fragment
handling, predictable mutation behavior, and errors precise enough for
callers to recover without scraping strings.

## Required checks

- `ruff check .` must pass with the full configured rule set.
- `pytest --cov=jsonptr --cov-branch --cov-fail-under=100` must keep
  line and branch coverage at 100%.
- `mypy --strict src/jsonptr` must pass with no hidden public API holes.
- The Python 3.9, 3.10, 3.11, and 3.12 GitHub Actions matrix must stay
  green.
- `python -m build` must produce installable wheel and sdist artifacts.
- Public behavior changes must include happy-path, edge-case, and error
  tests, plus README updates when behavior changes.

## Parser contract

- `parse` and `format_pointer` must round-trip every RFC 6901 token,
  including empty tokens and the `~0`/`~1` escape ordering.
- `parse_uri_fragment` and `format_uri_fragment` must round-trip RFC
  6901 URI-fragment examples, validate percent escapes, and reject
  invalid UTF-8.
- Resolution must reject `-` for reads; `set_value` may accept it only
  as the final token for append; `remove` must reject it.
- Error objects must keep structured fields (`pointer`, `path`,
  `token`, `detail`) useful for programmatic handling.

## Release checklist

- Run the required checks locally.
- Confirm GitHub Actions is green on the default branch.
- Confirm Dependabot and secret scanning have no open alerts.
- Confirm the README still describes the actual API and scope.
- Smoke-test the installed wheel with plain-pointer and URI-fragment
  examples before a release tag.
