---
name: json-schema-gen
description: Infer JSON Schema from sample JSON data with type detection and pattern recognition
version: 0.1.0
license: Apache-2.0
---

# JSON Schema Generator

## Purpose

Infer a JSON Schema from one or more sample JSON documents. Produces a schema with appropriate types, required fields, nullable detection, array item types, and pattern recognition for common formats (dates, emails, URLs, UUIDs).

## Quick Start

```bash
./scripts/run.sh sample.json
cat sample1.json sample2.json | ./scripts/run.sh --stdin --merge
```

## Reference Index

- **[references/api.md](references/api.md)** — Complete CLI interface documentation
- **[references/usage-guide.md](references/usage-guide.md)** — Step-by-step walkthrough of common use cases
- **[references/examples.md](references/examples.md)** — Concrete, copy-paste-ready examples

## Implementation

See `scripts/run.sh` (entry point) and `scripts/infer.py` (core logic).
