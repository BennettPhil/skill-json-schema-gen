#!/usr/bin/env python3
"""Infer JSON Schema from sample JSON data."""

import argparse
import json
import sys
from collections import Counter

def json_type(value):
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

def infer_schema(value):
    t = json_type(value)
    if t == "object":
        props = {}
        for k, v in value.items():
            props[k] = infer_schema(v)
        schema = {"type": "object", "properties": props}
        schema["required"] = sorted(value.keys())
        return schema
    elif t == "array":
        if not value:
            return {"type": "array"}
        item_schemas = [infer_schema(item) for item in value]
        merged = item_schemas[0]
        for s in item_schemas[1:]:
            merged = merge_schemas(merged, s)
        return {"type": "array", "items": merged}
    else:
        return {"type": t}

def merge_schemas(a, b):
    if a == b:
        return a
    ta = a.get("type")
    tb = b.get("type")

    # Different types -> anyOf
    if ta != tb:
        types = set()
        for s in [a, b]:
            if "anyOf" in s:
                for sub in s["anyOf"]:
                    types.add(sub.get("type", "string"))
            else:
                types.add(s.get("type", "string"))
        return {"anyOf": [{"type": t} for t in sorted(types)]}

    # Both objects
    if ta == "object":
        all_keys = set(list(a.get("properties", {}).keys()) + list(b.get("properties", {}).keys()))
        props = {}
        a_req = set(a.get("required", []))
        b_req = set(b.get("required", []))
        for k in all_keys:
            sa = a.get("properties", {}).get(k)
            sb = b.get("properties", {}).get(k)
            if sa and sb:
                props[k] = merge_schemas(sa, sb)
            elif sa:
                props[k] = sa
            else:
                props[k] = sb
        required = sorted(a_req & b_req & set(props.keys()))
        schema = {"type": "object", "properties": props}
        if required:
            schema["required"] = required
        return schema

    # Both arrays
    if ta == "array":
        ai = a.get("items")
        bi = b.get("items")
        if ai and bi:
            return {"type": "array", "items": merge_schemas(ai, bi)}
        return {"type": "array", "items": ai or bi or {}}

    return a

def main():
    parser = argparse.ArgumentParser(description="Infer JSON Schema from samples")
    parser.add_argument("files", nargs="*", help="JSON files (reads stdin if none)")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    samples = []
    if args.files:
        for f in args.files:
            with open(f) as fh:
                samples.append(json.load(fh))
    else:
        text = sys.stdin.read().strip()
        if not text:
            print('{"type": "object"}')
            return
        samples.append(json.loads(text))

    schema = infer_schema(samples[0])
    for s in samples[1:]:
        schema = merge_schemas(schema, infer_schema(s))

    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    if args.title:
        schema["title"] = args.title

    indent = None if args.compact else 2
    print(json.dumps(schema, indent=indent))

if __name__ == "__main__":
    main()
