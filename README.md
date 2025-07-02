# Clang Problem Matcher for GitHub Actions

This repository demonstrates how to use GitHub Actions problem matchers with Clang compiler diagnostics.

## Files

- `.github/clang-problem-matcher.json` - Basic problem matcher for Clang errors/warnings
- `.github/clang-multiline-matcher.json` - Enhanced matcher that handles multi-line output with code context
- `.github/workflows/test-clang-matcher.yml` - GitHub Actions workflow that tests the problem matcher
- `src/test.cpp` - C++ file with intentional errors to trigger Clang diagnostics

## Testing Locally

To test the Clang output locally:

```bash
clang++ -Wall -Werror -std=c++17 src/test.cpp -o test
```

This will produce errors similar to:
- Unknown sanitizer attribute warning/error
- Undefined variable error

## How the Problem Matcher Works

The problem matcher uses regex patterns to parse Clang output in the format:
```
file.cpp:line:column: severity: message [error-code]
    line | source code
         | ^~~~
```

The matcher extracts:
- File path
- Line number
- Column number
- Severity (error/warning/note)
- Error message
- Error code (e.g., -Wunknown-sanitizers)

## Using in Your Workflow

To use the problem matcher in your GitHub Actions workflow:

1. Add the matcher JSON file to `.github/` directory
2. Enable it with: `echo "::add-matcher::.github/clang-problem-matcher.json"`
3. Run your Clang compilation
4. Disable it with: `echo "::remove-matcher owner=clang::"`

## Testing on GitHub

1. Push this repository to GitHub
2. The workflow will run automatically on push
3. Check the Actions tab to see the annotations created by the problem matcher
4. Errors will be shown inline in pull requests