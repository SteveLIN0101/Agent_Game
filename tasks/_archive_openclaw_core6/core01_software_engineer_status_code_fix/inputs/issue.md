# Bug Report: API Returns 200 Instead of 201 Created

## Description
`create_resource()` returns HTTP 200 when it successfully creates a resource. Per REST conventions, it should return 201 Created. Client code checks for 201 to determine if a resource was newly created vs. already existing.

## Steps to Reproduce
```python
code, body = create_resource({"name": "test"})
print(code)  # Prints 200, should be 201
```

## Expected Behavior
- Successful creation → 201 Created
- Validation error → 400 Bad Request
- Deletion → 204 No Content

## Environment
Python 3.12
