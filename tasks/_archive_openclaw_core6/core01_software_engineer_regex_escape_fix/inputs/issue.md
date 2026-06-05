# Bug Report: Log Parser Regex Fails on Valid Log Lines

## Description
`parse_log_entry()` uses a regex pattern where special characters like `[`, `]`, `(`, `)` are not properly escaped. This causes valid log lines to fail to parse.

## Steps to Reproduce
```python
line = "[INFO] [2025-01-15 10:30:00] User login (user=alice, ip=192.168.1.1)"
result = parse_log_entry(line)
print(result)  # Expected dict, got None
```

## Expected Behavior
The function should correctly parse log lines with the format:
`[LEVEL] [timestamp] message (key=value, ...)`

## Notes
- `[` and `]` are regex metacharacters (character class)
- `(` and `)` are regex metacharacters (capture group)
- They must be escaped with `\` to match literal brackets/parentheses

## Environment
Python 3.12
