# Usage Guide

> Step-by-step guide to using json-schema-gen.

## Prerequisites

- Python 3.7+
- Bash

## Getting Started

### Step 1: Generate a Schema from a Single File

```bash
./scripts/run.sh user.json
```

This reads `user.json`, infers types for every field, and outputs a JSON Schema.

### Step 2: Merge Multiple Samples

When you have multiple JSON examples, merge them to get a more accurate schema:

```bash
./scripts/run.sh user1.json user2.json user3.json --merge
```

Fields present in all samples are marked `required`. Fields missing from some samples become optional.

### Step 3: Detect Patterns

By default, string values are checked against common patterns:

- ISO 8601 dates → `format: "date-time"`
- Email addresses → `format: "email"`
- URLs → `format: "uri"`
- UUIDs → `format: "uuid"`

Disable with `--no-patterns`.

## Common Tasks

### Infer Schema from API Response

```bash
curl -s https://api.example.com/users/1 | ./scripts/run.sh --stdin --title "User"
```

### Set Required Threshold

If a field appears in 80% or more of your samples, mark it required:

```bash
./scripts/run.sh *.json --merge --required-threshold 0.8
```

## Troubleshooting

### Invalid JSON Input

**Symptom**: Error message about JSON parsing.
**Cause**: Input file is not valid JSON.
**Fix**: Validate your JSON with `python3 -m json.tool < file.json`.
