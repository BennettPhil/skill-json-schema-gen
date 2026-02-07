#!/usr/bin/env python3
"""Infer JSON Schema from sample JSON data."""

import argparse
import json
import re
import sys

DRAFT_URLS = {
    "2020-12": "https://json-schema.org/draft/2020-12/schema",
    "7": "http://json-schema.org/draft-07/schema#",
    "4": "http://json-schema.org/draft-04/schema#",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_RE = re.compile(r"^https?://[^\s]+$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def detect_format(value):
    """Detect common string formats."""
    if UUID_RE.match(value):
        return "uuid"
    if EMAIL_RE.match(value):
        return "email"
    if URL_RE.match(value):
        return "uri"
    if DATE_RE.match(value):
        return "date-time"
    return None


def json_type(value):
    """Get JSON Schema type for a Python value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def infer_schema(value, detect_patterns=True):
    """Infer a schema from a single value."""
    if value is None:
        return {"type": "null"}

    t = json_type(value)

    if t == "object":
        props = {}
        required = sorted(value.keys())
        for k, v in value.items():
            props[k] = infer_schema(v, detect_patterns)
        schema = {"type": "object", "properties": props}
        if required:
            schema["required"] = required
        return schema

    if t == "array":
        if not value:
            return {"type": "array", "items": {}}
        item_schemas = [infer_schema(item, detect_patterns) for item in value]
        merged = merge_schemas(item_schemas)
        return {"type": "array", "items": merged}

    if t == "string" and detect_patterns:
        fmt = detect_format(value)
        if fmt:
            return {"type": "string", "format": fmt}

    return {"type": t}


def merge_type(types):
    """Merge a list of type values into one."""
    flat = set()
    for t in types:
        if isinstance(t, list):
            flat.update(t)
        else:
            flat.add(t)
    if len(flat) == 1:
        return flat.pop()
    return sorted(flat)


def merge_schemas(schemas):
    """Merge multiple schemas into one that accepts all."""
    if not schemas:
        return {}
    if len(schemas) == 1:
        return schemas[0]

    types = [s.get("type", "string") for s in schemas]
    type_set = set()
    for t in types:
        if isinstance(t, list):
            type_set.update(t)
        else:
            type_set.add(t)

    # All same type
    if len(type_set) == 1 and "object" in type_set:
        return merge_object_schemas(schemas)
    if len(type_set) == 1 and "array" in type_set:
        item_schemas = [s.get("items", {}) for s in schemas]
        return {"type": "array", "items": merge_schemas(item_schemas)}
    if type_set == {"object", "null"}:
        obj_schemas = [s for s in schemas if s.get("type") != "null"]
        merged = merge_object_schemas(obj_schemas) if obj_schemas else {"type": "object"}
        merged["type"] = ["object", "null"]
        return merged

    # Mixed types
    merged_type = merge_type(types)
    result = {"type": merged_type}

    # Preserve format if all string schemas agree
    formats = [s.get("format") for s in schemas if s.get("type") == "string" and "format" in s]
    if formats and len(set(formats)) == 1:
        result["format"] = formats[0]

    return result


def merge_object_schemas(schemas, required_threshold=1.0):
    """Merge multiple object schemas."""
    all_keys = {}
    key_counts = {}
    total = len(schemas)

    for s in schemas:
        props = s.get("properties", {})
        for k, v in props.items():
            if k not in all_keys:
                all_keys[k] = []
                key_counts[k] = 0
            all_keys[k].append(v)
            key_counts[k] += 1

    merged_props = {}
    required = []

    for k, sub_schemas in all_keys.items():
        merged_props[k] = merge_schemas(sub_schemas)
        fraction = key_counts[k] / total
        if fraction >= required_threshold:
            required.append(k)

    result = {"type": "object", "properties": merged_props}
    if required:
        result["required"] = sorted(required)
    return result


def infer_from_samples(samples, detect_patterns=True, required_threshold=1.0):
    """Infer schema from multiple samples."""
    if not samples:
        return {}

    schemas = [infer_schema(s, detect_patterns) for s in samples]

    if len(schemas) == 1:
        return schemas[0]

    # Check if all are objects
    all_objects = all(s.get("type") == "object" for s in schemas)
    if all_objects:
        return merge_object_schemas(schemas, required_threshold)

    return merge_schemas(schemas)


def main():
    parser = argparse.ArgumentParser(description="Infer JSON Schema from samples")
    parser.add_argument("files", nargs="*", help="JSON files")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--merge", action="store_true", help="Merge multiple docs")
    parser.add_argument("--no-patterns", action="store_true", help="Disable patterns")
    parser.add_argument("--required-threshold", type=float, default=1.0)
    parser.add_argument("--title", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--draft", default="2020-12", choices=["2020-12", "7", "4"])
    args = parser.parse_args()

    detect_patterns = not args.no_patterns
    samples = []

    if args.stdin:
        content = sys.stdin.read().strip()
        if not content:
            print("Error: Empty input.", file=sys.stderr)
            sys.exit(1)
        try:
            data = json.loads(content)
            if args.merge and isinstance(data, list):
                samples.extend(data)
            else:
                samples.append(data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        for fpath in args.files:
            try:
                with open(fpath) as f:
                    data = json.load(f)
                samples.append(data)
            except FileNotFoundError:
                print(f"Error: File not found: {fpath}", file=sys.stderr)
                sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in {fpath}: {e}", file=sys.stderr)
                sys.exit(1)

    if not samples:
        print("Error: No samples provided.", file=sys.stderr)
        sys.exit(1)

    if args.merge and len(samples) > 1:
        schema = infer_from_samples(samples, detect_patterns, args.required_threshold)
    else:
        schema = infer_schema(samples[0], detect_patterns)

    schema["$schema"] = DRAFT_URLS.get(args.draft, DRAFT_URLS["2020-12"])
    if args.title:
        schema["title"] = args.title

    # Move $schema and title to front
    ordered = {"$schema": schema.pop("$schema")}
    if "title" in schema:
        ordered["title"] = schema.pop("title")
    ordered.update(schema)

    result = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
