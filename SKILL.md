---
name: json-schema-gen
description: Infers a JSON Schema from one or more sample JSON documents, supporting type detection, required fields, and array item schemas.
version: 0.1.0
license: Apache-2.0
---

# JSON Schema Generator

Infers a JSON Schema (draft-07) from one or more sample JSON documents. Detects types, required fields, nested objects, array item schemas, and enum-like values.

## Usage

```bash
# Infer schema from a single file
./scripts/run.sh sample.json

# Infer from multiple samples (merges schemas)
./scripts/run.sh sample1.json sample2.json

# Read from stdin
cat data.json | ./scripts/run.sh

# Pretty or compact output
./scripts/run.sh --compact sample.json
```

## Options

- `--compact` — Output compact JSON (no indentation)
- `--title TITLE` — Set the schema title
- `--help` — Show usage information

## Features

- Detects string, number, integer, boolean, null, object, and array types
- Infers `required` fields by checking which keys appear in all samples
- Merges multiple samples to produce a union schema
- Detects array item types (homogeneous arrays get typed `items`)
- Nested objects produce nested schemas recursively
