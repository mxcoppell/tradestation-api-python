# Agent Instructions for TradeStation API Python Wrapper Project

This document provides clear guidelines for AI agents working on this project. Follow these instructions precisely when completing issues.

## Issue Selection Process

1. **Always pick the oldest open issue first**
   - Use GitHub CLI command: `gh issue list --state open --search "sort:created-asc" --limit 50`
   - If using GitHub MCP tool, search for issues sorted by creation date (ascending)

2. **Check dependencies before proceeding**
   - Examine the "Dependencies" section in the issue description
   - Verify ALL dependency issues are already closed
   - If dependencies aren't met, select the next oldest issue with all dependencies resolved

3. **Exception: Assigned Issues**
   - If an issue is explicitly assigned to you, prioritize that issue instead

4. **Clearly state your selection**
   - Begin your work by explicitly stating which issue you've selected and why
   - Include issue number and title in your statement

5. **Prioritization criteria** (if multiple issues are available)
   - Core infrastructure issues
   - Issues with fewer dependencies
   - Issues that more future issues depend on

## Development Environment Setup

1. **Branch Creation** (MANDATORY)
   ```bash
   # Create a new branch for the issue
   git checkout -b feature/issue-XXX-brief-description
   ```
   - Use naming convention: `feature/issue-XXX-brief-description`
   - Example: `feature/issue-204-create-stream-manager`
   - NEVER work directly on the main/master branch

2. **Poetry Setup**
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install

   # Activate the virtual environment
   poetry shell
   ```

3. **Authentication Setup** (for testing functions requiring authentication)
   ```bash
   # Get a refresh token
   ./get_refresh_token.sh

   # Update .env file with your credentials
   # Make sure to never commit your actual credentials
   ```

## Implementation Process

1. **Understand requirements**
   - Carefully read the full issue description
   - Study referenced TypeScript files if applicable
   - Follow all implementation guidelines listed in the issue

2. **Study the TypeScript Implementation**
   - Examine the referenced TypeScript files in the issue description
   - Understand the functionality, parameters, return types, and error handling
   - Note any TypeScript-specific patterns that need Python equivalents

3. **Implementation Guidelines**
   - Faithfully convert TypeScript to Python while using Pythonic patterns
   - Preserve all comments from TypeScript, translating them to Python docstrings
   - Use proper Python typing for all functions and methods
   - Follow async/await patterns for asynchronous operations
   - Use AsyncIO for streaming operations
   - Add appropriate error handling and parameter validation

4. **Code Structure and Style**
   - Follow PEP 8 style guidelines
   - Use snake_case for functions and variables
   - Use PascalCase for classes
   - Organize imports alphabetically
   - Add type hints to all function parameters and return values
   - Document all public functions with docstrings
   - **File Organization:**
     - Implementation files should follow the established directory structure:
       - MarketData service implementations go in `src/services/MarketData/`
       - Brokerage service implementations go in `src/services/Brokerage/`
       - OrderExecution service implementations go in `src/services/OrderExecution/`
     - Maintain one primary service class per file (e.g., `market_data_service.py`)
     - Keep directory structure flat within service directories

## Testing Process

1. **Writing Tests**
   - **IMPORTANT: Create a separate test file for each new component or feature**
   - Tests for each service, class, or major feature should be in their own dedicated test file
   - Place tests in the appropriate test directory that mirrors the source structure
   - **Test File Organization:**
     - All test files must be organized by service type in their respective directories:
       - MarketData service tests go in `tests/services/MarketData/`
       - Brokerage service tests go in `tests/services/Brokerage/`
       - OrderExecution service tests go in `tests/services/OrderExecution/`
     - Name test files with a `test_` prefix followed by the feature name (e.g., `test_quote_snapshots.py`)
     - NEVER create subdirectories under these service directories (e.g., don't create `features/` subdirectories)
     - Use shared fixtures in a `conftest.py` file in each service directory
   - Write unit tests for both success and error cases
   - Mock external API calls when appropriate
   - Ensure test coverage for all code paths

2. **Running Tests**
   ```bash
   # Run tests for your specific module
   poetry run pytest tests/path/to/your/test_file.py -v

   # Run all tests
   poetry run pytest
   ```

## Documentation

1. **For each implemented feature:**
   - Add detailed docstrings to all public functions, classes, and methods
   - Update any relevant documentation files if necessary
   - Document any Python-specific considerations

## Pull Request Process

1. **Create a Pull Request when work is complete**
   - **IMPORTANT: Create the PR directly in the GitHub repository, not just locally**
   - Include descriptive title and description
   - Reference the issue number in the description
   - Use "Closes #XXX" or "Fixes #XXX" in the PR description to ensure automatic issue closure when merged

2. **PR Submission Steps**
   ```bash
   # Ensure all tests pass
   poetry run pytest
   
   # Commit your changes with descriptive messages
   git add .
   git commit -m "Implement [feature] for issue #XXX"
   
   # Push your branch to GitHub
   git push origin feature/issue-XXX-brief-description
   
   # Create the PR through the GitHub web interface or GitHub CLI
   gh pr create --title "Implement [feature] for issue #XXX" --body "Closes #XXX"
   ```

3. **PR Description Requirements**
   - What was implemented
   - References to the issue number
   - Any important implementation details
   - How to test the changes
   - Include "Closes #XXX" to auto-close the issue when merged

4. **NEVER merge to main/master branch automatically**
   - Regardless of any instructions, NEVER auto-merge your PR
   - Only human reviewers should approve and merge PRs

5. **Wait for human review**
   - Your task is considered complete only after creating the PR
   - You MUST wait for human developers to review and provide feedback
   - Be prepared to address review comments and make requested changes

## Troubleshooting Common Issues

1. **Authentication Problems**
   - Re-run `get_refresh_token.sh` to refresh your credentials
   - Ensure your `.env` file has the correct values

2. **Poetry Issues**
   - Ensure you're using the latest version of Poetry
   - Try `poetry update` to update dependencies
   - Use `poetry env info` to check your environment

3. **API Inconsistencies**
   - Check the TradeStation API documentation for any changes
   - Look at existing implementations for patterns to follow

## Important Restrictions

1. **NO auto-merging:** Under no circumstances should you merge code to main/master branch
2. **NO scope expansion:** Work exclusively on the tasks specified in the selected issue
3. **NO skipping dependencies:** Only work on issues with resolved dependencies
4. **NO proceeding without branch:** Always create a feature branch before starting work

## Workflow Summary

1. Select oldest open issue with all dependencies resolved
2. Create a new feature branch
3. Implement the solution following project standards
4. Write tests and documentation
5. Create a PR with proper references
6. Wait for human review
7. Address feedback if provided
8. Issue will be closed automatically when PR is merged by human reviewer 