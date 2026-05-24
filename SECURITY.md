# Security policy

## Supported versions

The `main` branch is the supported development line for `jsonptr`.

## Reporting a vulnerability

Please report dependency issues, malformed-input crashes, or other security concerns through GitHub's private vulnerability reporting when available, or by opening a minimal public issue without exploit payloads.

Useful reports include:

- Inputs that trigger crashes, runaway runtime, or memory exhaustion
  while parsing pointer strings or URI fragments.
- Cases where invalid `~` escapes, invalid percent escapes, invalid
  UTF-8, or non-canonical array indices are accepted accidentally.
- Mutations where `set_value` or `remove` writes/removes a different
  location than the pointer identifies.

For untrusted input, callers should still enforce reasonable request
and document-size limits before invoking this project. `jsonptr` does
not parse JSON text, stream data from the network, or validate schemas;
it only interprets pointer strings against Python containers already in
memory.
