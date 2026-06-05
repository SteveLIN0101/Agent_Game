# Bug Report: CSV Export Column Data Swapped

## Description
When exporting users to CSV, the `email` column contains `username` data and the `username` column contains `email` data. The row data is written in the wrong order.

## Steps to Reproduce
```python
users = [{"id": "1", "username": "alice", "email": "alice@example.com", "created_at": "2025-01-01"}]
csv_text = export_to_csv(users)
# email column shows "alice", username column shows "alice@example.com"
```

## Expected Behavior
Each column should contain the data matching its header name.

## Environment
Python 3.12
