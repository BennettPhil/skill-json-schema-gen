#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat >&2 <<'EOF'
Usage: run.sh [OPTIONS] [FILE...]

Infer a JSON Schema from sample JSON documents.

Options:
    --compact       Compact JSON output
    --title TITLE   Set schema title
    -h, --help      Show this help
EOF
    exit "${1:-0}"
}

COMPACT=""
TITLE=""
FILES=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --compact) COMPACT="--compact"; shift ;;
        --title) TITLE="$2"; shift 2 ;;
        -h|--help) usage 0 ;;
        -*) echo "Unknown option: $1" >&2; usage 1 ;;
        *) FILES+=("$1"); shift ;;
    esac
done

exec python3 "$SCRIPT_DIR/infer.py" $COMPACT ${TITLE:+--title "$TITLE"} "${FILES[@]}"
