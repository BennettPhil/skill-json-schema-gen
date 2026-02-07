# API Reference

> Complete interface documentation for json-schema-gen.

## Commands

### `run.sh`

**Description**: Infer a JSON Schema from sample JSON data.

**Usage**:
```
run.sh [OPTIONS] [FILE...]
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| `FILE` | No | One or more JSON files to analyze. Omit if using `--stdin`. |

**Options**:
| Option | Default | Description |
|--------|---------|-------------|
| `--stdin` | false | Read JSON from stdin |
| `--merge` | false | Merge multiple JSON documents into one schema |
| `--detect-patterns` | true | Detect date, email, URL, UUID patterns |
| `--no-patterns` | — | Disable pattern detection |
| `--required-threshold <n>` | 1.0 | Fraction of samples where a field must appear to be required (0.0-1.0) |
| `--title <string>` | — | Set the schema title |
| `--output <path>` | stdout | Write schema to a file |
| `--draft <version>` | 2020-12 | JSON Schema draft version (2020-12, 7, 4) |
| `--help` | — | Show usage information |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid input or error |

**Example**:
```bash
run.sh sample.json --title "User Schema" --output schema.json
```
