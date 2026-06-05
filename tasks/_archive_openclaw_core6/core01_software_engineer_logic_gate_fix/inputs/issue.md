# Bug Report: Admin Users Denied Access

## Description
A user with the "admin" role AND "read" permission on a resource is being denied access. The issue is in the boolean logic of `can_access()`.

## Steps to Reproduce
```python
can_access("alice", "dashboard", role="admin", permissions=["read"])
# Returns False, but should return True (admin can access everything)
```

## Expected Behavior
- Admin users should access any resource regardless of permissions
- Non-admin users should access only if they have "read" permission

## Current Behavior
Admin + read → denied (wrong!)
User + read → allowed (correct)
Admin + no read → denied (wrong! should allow)

## Environment
Python 3.12
