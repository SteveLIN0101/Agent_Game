# Known Data Issues

1. **Duplicate payments**: Some payment records have identical transaction_ids. For duplicates, keep the record with the most recent timestamp.

2. **Missing end_dates**: Subscriptions without an end_date are considered active.

3. **Currency**: All amounts are in USD unless otherwise noted.
