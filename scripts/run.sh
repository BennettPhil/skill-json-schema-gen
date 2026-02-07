#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
Usage: run.sh [OPTIONS] [FILE...]

Infer a JSON Schema from sample JSON data.

Arguments:
  FILE                     One or more JSON files to analyze

Options:
  --stdin                  Read JSON from stdin
  --merge                  Merge multiple documents into one schema
  --no-patterns            Disable pattern detection (date, email, URL, UUID)
  --required-threshold <n> Fraction for required fields (default: 1.0)
  --title <string>         Set the schema title
  --output <path>          Write to file instead of stdout
  --draft <version>        JSON Schema draft (2020-12, 7, 4). Default: 2020-12
  --help                   Show this help message
USAGE
}

ARGS=()
FILES=()
FROM_STDIN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stdin) FROM_STDIN=true; ARGS+=("--stdin"); shift ;;
    --merge) ARGS+=("--merge"); shift ;;
    --no-patterns) ARGS+=("--no-patterns"); shift ;;
    --required-threshold) ARGS+=("--required-threshold" "$2"); shift 2 ;;
    --title) ARGS+=("--title" "$2"); shift 2 ;;
    --output) ARGS+=("--output" "$2"); shift 2 ;;
    --draft) ARGS+=("--draft" "$2"); shift 2 ;;
    --help) usage; exit 0 ;;
    -*) echo "Error: Unknown option: $1" >&2; usage >&2; exit 1 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

if [ "$FROM_STDIN" = false ] && [ ${#FILES[@]} -eq 0 ]; then
  echo "Error: Provide input files or use --stdin." >&2
  usage >&2
  exit 1
fi

if [ "$FROM_STDIN" = true ]; then
  python3 "$SCRIPT_DIR/infer.py" "${ARGS[@]}"
else
  python3 "$SCRIPT_DIR/infer.py" "${ARGS[@]}" "${FILES[@]}"
fi
