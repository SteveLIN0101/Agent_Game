# Bug Report: Crash When Preferences Key Missing

## Description
When `config.json` contains a `preferences` key set to `null` (or omits it entirely), the application crashes with:

```
AttributeError: 'NoneType' object has no attribute 'get'
```

## Steps to Reproduce
1. Create a config.json with `{"theme": "dark"}` (no preferences key)
2. Call `get_user_config("config.json")`
3. App crashes

## Expected Behavior
Should return default preferences `{"notifications": True, "auto_save": False}` when preferences is missing.

## Environment
- Python 3.12
- All OS
