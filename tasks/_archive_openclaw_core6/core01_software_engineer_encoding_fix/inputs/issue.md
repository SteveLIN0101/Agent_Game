# Bug Report: UnicodeDecodeError When Reading Config Files

## Description
`read_config_file()` crashes with `UnicodeDecodeError` when reading config files containing non-ASCII characters (Chinese, Japanese, accented characters, etc.).

## Steps to Reproduce
1. Create a config file with UTF-8 content: `name=张三`
2. Call `read_config_file("config.txt")`
3. App crashes with UnicodeDecodeError

## Expected Behavior
Should handle UTF-8 encoded files correctly by specifying encoding='utf-8'.

## Environment
Python 3.12, Windows/Linux/macOS
