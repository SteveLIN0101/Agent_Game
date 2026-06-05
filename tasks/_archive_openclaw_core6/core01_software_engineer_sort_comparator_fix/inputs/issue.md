# Bug Report: Date Sorting Returns Wrong Order

## Description
`sort_by_date()` returns dates in descending order when `ascending=True`, and in ascending order when `ascending=False`. The comparator function has inverted return values.

## Steps to Reproduce
```python
items = [
    {"name": "C", "date": date(2025, 3, 1)},
    {"name": "A", "date": date(2025, 1, 1)},
    {"name": "B", "date": date(2025, 2, 1)},
]
result = sort_by_date(items, ascending=True)
# Expected: A(Jan), B(Feb), C(Mar)
# Actual: C(Mar), B(Feb), A(Jan) — reversed!
```

## Expected Behavior
- `ascending=True` → earliest date first
- `ascending=False` → latest date first

## Environment
Python 3.12
