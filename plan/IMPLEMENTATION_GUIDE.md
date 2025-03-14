# Implementation Guide for Agents

This document provides guidance on how to select and complete issues for the TradeStation API Python wrapper project.

## Issue Selection Process

### Understanding Dependencies

Issues in this project have dependencies which must be completed before working on a particular issue. When selecting an issue:

1. Look at the "Dependencies" section in the issue description
2. Check if all dependency issues (e.g., #196, #197) are already closed
3. Only select issues where all dependencies have been met
4. Start with foundational issues (lower numbers) and progress to more dependent issues

### Finding Available Issues

1. Go to the [Issues tab](https://github.com/mxcoppell/tradestation-api-python/issues)
2. Filter for open issues by clicking on "Open" filter
3. Check the "Dependencies" section of each issue
4. Choose an issue where all dependencies are already completed
5. If multiple issues are available, prioritize:
   - Core infrastructure issues
   - Issues with fewer dependencies
   - Issues that more future issues depend on

## Development Environment Setup

### Initial Repository Setup

```bash
# Clone the repository
git clone https://github.com/mxcoppell/tradestation-api-python.git
cd tradestation-api-python

# Create a new branch for the issue
git checkout -b feature/issue-XXX-brief-description
```

### Poetry Setup

We use Poetry for dependency management:

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Authentication Setup

For testing functions that require authentication:

```bash
# Get a refresh token
./get_refresh_token.sh

# Update .env file with your credentials
# Make sure to never commit your actual credentials
```

## Implementation Process

### 1. Understand the Issue Requirements

Each issue will contain:
- Task details explaining what needs to be implemented
- Source TypeScript files to reference
- Implementation requirements with specific guidelines
- Dependencies on other issues
- Development instructions

### 2. Study the TypeScript Implementation

1. Examine the referenced TypeScript files in the issue description
2. Understand the functionality, parameters, return types, and error handling
3. Note any TypeScript-specific patterns that need Python equivalents

### 3. Implementation Guidelines

- Faithfully convert TypeScript to Python while using Pythonic patterns
- Preserve all comments from TypeScript, translating them to Python docstrings
- Use proper Python typing for all functions and methods
- Follow async/await patterns for asynchronous operations
- Use AsyncIO for streaming operations
- Add appropriate error handling and parameter validation

### 4. Code Structure and Style

- Follow PEP 8 style guidelines
- Use snake_case for functions and variables
- Use PascalCase for classes
- Organize imports alphabetically
- Add type hints to all function parameters and return values
- Document all public functions with docstrings

## Testing Process

### Writing Tests

1. Create tests in the appropriate test directory
2. Write unit tests for both success and error cases
3. Mock external API calls when appropriate
4. Ensure test coverage for all code paths

### Running Tests

```bash
# Run tests for your specific module
poetry run pytest tests/path/to/your/test_file.py -v

# Run all tests
poetry run pytest
```

## Documentation

For each implemented feature:
1. Add detailed docstrings to all public functions, classes, and methods
2. Update any relevant documentation files if necessary
3. Document any Python-specific considerations

## Pull Request Submission

1. Ensure all tests pass
2. Commit your changes with descriptive messages
   ```bash
   git add .
   git commit -m "Implement [feature] for issue #XXX"
   ```
3. Push your branch
   ```bash
   git push origin feature/issue-XXX-brief-description
   ```
4. Create a pull request with a description that includes:
   - What was implemented
   - References to the issue number
   - Any important implementation details
   - How to test the changes
5. Include "Closes #XXX" in the PR description to auto-close the issue when merged

## Completing the Issue

1. After your PR is approved and merged, the issue will be closed automatically
2. If not closed automatically, update the issue with a comment linking to the merged PR
3. Set the issue status to "Closed"

## Troubleshooting Common Issues

### Authentication Problems
- Re-run `get_refresh_token.sh` to refresh your credentials
- Ensure your `.env` file has the correct values

### Poetry Issues
- Ensure you're using the latest version of Poetry
- Try `poetry update` to update dependencies
- Use `poetry env info` to check your environment

### API Inconsistencies
- Check the TradeStation API documentation for any changes
- Look at existing implementations for patterns to follow

Remember that the goal is to create a Python implementation that matches the functionality of the TypeScript version while following Python best practices. 