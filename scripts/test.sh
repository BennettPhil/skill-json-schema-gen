#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
PASS=0
FAIL=0

check() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc"
        echo "    expected: $expected"
        echo "    actual:   $actual"
        FAIL=$((FAIL + 1))
    fi
}

check_contains() {
    local desc="$1" needle="$2" haystack="$3"
    if echo "$haystack" | grep -qF -- "$needle"; then
        echo "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $desc (not found: '$needle')"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== json-schema-gen tests ==="

# Test 1: simple object
echo '{"name": "Alice", "age": 30}' > "$TMPDIR/t1.json"
out=$(python3 "$SCRIPT_DIR/infer.py" "$TMPDIR/t1.json")
check_contains "detects object type" '"type": "object"' "$out"
check_contains "detects string prop" '"type": "string"' "$out"
check_contains "detects integer prop" '"type": "integer"' "$out"
check_contains "has name in properties" '"name"' "$out"

# Test 2: array detection
echo '{"items": [1, 2, 3]}' > "$TMPDIR/t2.json"
out2=$(python3 "$SCRIPT_DIR/infer.py" "$TMPDIR/t2.json")
check_contains "detects array type" '"type": "array"' "$out2"

# Test 3: stdin input
out3=$(echo '{"ok": true}' | python3 "$SCRIPT_DIR/infer.py")
check_contains "stdin: detects boolean" '"type": "boolean"' "$out3"
check_contains "stdin: has schema ref" 'draft-07' "$out3"

# Test 4: --title flag
out4=$(echo '{}' | python3 "$SCRIPT_DIR/infer.py" --title "MySchema")
check_contains "--title sets title" '"title": "MySchema"' "$out4"

# Test 5: multiple samples merge required
echo '{"a": 1, "b": 2}' > "$TMPDIR/s1.json"
echo '{"a": 3, "c": 4}' > "$TMPDIR/s2.json"
out5=$(python3 "$SCRIPT_DIR/infer.py" "$TMPDIR/s1.json" "$TMPDIR/s2.json")
check_contains "merged: has a in required" '"a"' "$out5"

# Test 6: --help exits 0
bash "$SCRIPT_DIR/run.sh" --help >/dev/null 2>&1 && code=0 || code=$?
check "--help exits 0" "0" "$code"

# Test 7: compact output
out7=$(echo '{"x": 1}' | python3 "$SCRIPT_DIR/infer.py" --compact)
# Compact output should not have newlines between braces
lines=$(echo "$out7" | wc -l | tr -d ' ')
check "compact is single line" "1" "$lines"

echo ""
echo "$PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
