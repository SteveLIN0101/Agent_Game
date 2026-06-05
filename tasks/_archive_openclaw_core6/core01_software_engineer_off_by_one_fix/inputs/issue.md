# Bug Report: Task Scheduler Misses Last Task

## Description
When scheduling n tasks, only n-1 tasks are actually assigned to workers. The last task is always missed.

## Steps to Reproduce
```python
from scheduler import schedule_tasks
tasks = schedule_tasks(10)
print(len(tasks))  # Prints 9, should be 10
```

## Expected Behavior
`schedule_tasks(n)` should return exactly n assignments.

## Environment
- Python 3.12
