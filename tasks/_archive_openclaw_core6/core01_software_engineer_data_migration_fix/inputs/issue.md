# Bug Report: Data Migration Silently Drops Rows

## Description
`migrate_data()` uses `zip()` to pair users with orders. When the two lists have different lengths, `zip()` silently truncates to the shorter list, causing data loss without any error or warning.

## Steps to Reproduce
```python
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, {"id": 3, "name": "Charlie"}]
orders = [{"id": 101, "amount": 50.0}, {"id": 102, "amount": 75.0}]
result = migrate_data(users, orders)
print(len(result))  # Prints 2, but 3 users exist — Charlie's data is lost!
```

## Expected Behavior
The migration should preserve ALL rows from BOTH tables, using a proper LEFT JOIN approach. Users without orders should still appear (with null/empty order fields), and orders without matching users should also appear.

## Environment
Python 3.12
