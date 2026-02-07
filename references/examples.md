# Examples

> Concrete, copy-paste-ready examples for json-schema-gen.

## Basic Usage

### Simple Object

Input (`user.json`):
```json
{"name": "Alice", "age": 30, "active": true}
```

```bash
./scripts/run.sh user.json
```

Output:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"},
    "active": {"type": "boolean"}
  },
  "required": ["name", "age", "active"]
}
```

### Nested Objects

Input:
```json
{"user": {"name": "Bob", "address": {"city": "Portland", "zip": "97201"}}}
```

Output includes nested `properties` with their own `type: "object"`.

### Arrays

Input:
```json
{"tags": ["go", "rust"], "scores": [95, 87, 92]}
```

Output:
```json
{
  "properties": {
    "tags": {"type": "array", "items": {"type": "string"}},
    "scores": {"type": "array", "items": {"type": "integer"}}
  }
}
```

## Pattern Detection

Input:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "website": "https://example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

Output detects formats:
```json
{
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "email": {"type": "string", "format": "email"},
    "website": {"type": "string", "format": "uri"},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

## Merging Multiple Samples

```bash
echo '{"name": "Alice", "age": 30}' > /tmp/s1.json
echo '{"name": "Bob", "nickname": "Bobby"}' > /tmp/s2.json
./scripts/run.sh /tmp/s1.json /tmp/s2.json --merge
```

Result: `name` is required (in both), `age` and `nickname` are optional.

## Nullable Fields

Input:
```json
{"name": "Alice", "bio": null}
```

Output:
```json
{
  "properties": {
    "name": {"type": "string"},
    "bio": {"type": ["string", "null"]}
  }
}
```
