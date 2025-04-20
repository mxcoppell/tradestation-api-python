# Agent Instructions for TradeStation API Python Wrapper Project

This document provides clear guidelines for AI agents working on this project. Follow these instructions precisely when completing issues.

## Issue Selection Process

1. **Always pick the oldest open issue first**
   - Use GitHub CLI command: `gh issue list --state open --search "sort:created-asc" --limit 50`

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

1. **Update Main Branch** (MANDATORY)
   ```bash
   # Ensure you're on the main branch
   git checkout main

   # Pull the latest changes
   git pull
   ```

2. **Branch Creation** (MANDATORY)
   ```bash
   # Create a new branch for the issue
   git checkout -b feature/issue-XXX-brief-description
   ```
   - Use naming convention: `feature/issue-XXX-brief-description`
   - Example: `feature/issue-204-create-stream-manager`
   - NEVER work directly on the main/master branch

3. **Poetry Setup**
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -

   # Install dependencies
   poetry install

   # Activate the virtual environment
   poetry shell
   ```

4. **Authentication Setup & Verification** (MANDATORY before running examples/tests requiring auth)
   
   a. **Check `.env` File:**
      - **BEFORE** attempting to run any example script or test that requires authentication, you MUST verify that the `.env` file in the project root contains valid values for:
        - `CLIENT_ID`
        - `REFRESH_TOKEN`
        - `ENVIRONMENT` (e.g., `simulation` or `live`)
      - If any of these variables are missing or empty, **STOP** and inform the user they need to update the `.env` file with their credentials and environment settings.
      - **DO NOT PROCEED** with running the authenticated script/test until the user confirms the `.env` file is updated.

   b. **Security Reminder:**
      - Always ensure the actual `.env` file is listed in `.gitignore` and never commit your actual credentials to the repository.

## Implementation Process

1. **Understand requirements**
   - Carefully read the full issue description
   - Study referenced TypeScript files if applicable
   - Follow all implementation guidelines listed in the issue
   - For each issue, plan both the implementation and its corresponding test files

2. **Study the TypeScript Implementation**
   - Examine the referenced TypeScript files in the issue description
   - Understand the functionality, parameters, return types, and error handling
   - Note any TypeScript-specific patterns that need Python equivalents
   - Pay attention to how features are separated in the TypeScript codebase

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
     - Each issue should have its own dedicated test file(s)
     - NEVER add tests for a new feature to an existing test file for a different feature
     - If implementing a method in `MarketDataService`, create a new test file like `test_your_feature_name.py`
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
   - **Examples of correct test file organization:**
     - For issue "Implement get_quote_snapshots": Create `tests/services/MarketData/test_quote_snapshots.py`
     - For issue "Implement get_positions": Create `tests/services/Brokerage/test_positions.py`
     - For issue "Implement place_order": Create `tests/services/OrderExecution/test_place_order.py`

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
   - **ALWAYS include any updates to `CONTINUOUS-SELF-LEARNING.md` as part of your PR if you've added new knowledge**

2. **PR Submission Steps**
   ```bash
   # Ensure all tests pass
   poetry run pytest
   
   # **CRITICAL: If the issue created/modified an example script:**
   # Run the example from the project root to ensure it executes without errors 
   # and produces the expected/correct output. 
   # Example: poetry run python examples/YourService/your_example.py
   # **MUST fix any errors discovered during execution before proceeding!**

   # Commit your changes with descriptive messages
   git add .
   git commit -m "Implement [feature] for issue #XXX"
   
   # Push your branch to GitHub
   git push origin feature/issue-XXX-brief-description
   
   # Create the PR through the GitHub web interface or GitHub CLI
   gh pr create --title "Implement [feature] for issue #XXX" --body "Closes #XXX"
   ```

   **CRITICAL: When creating the PR through GitHub CLI or web interface, you MUST include "Closes #XXX" or "Fixes #XXX" at the BOTTOM of the PR description.** GitHub specifically looks for these keywords followed by the issue number to create the automatic link for closing issues. The issue closing reference MUST be:
   - **MUST BE ON ITS OWN SEPARATE LINE with nothing else on that line**
   - At the bottom of the PR description
   - Using one of these exact keywords: "Closes", "Fixes", "Resolves" (followed by #issue_number)
   - Example: `Closes #123` or `Fixes #123` or `Resolves #123`

   **RECOMMENDED WORKFLOW FOR PR DESCRIPTIONS:**
   
   Follow these exact steps to create a comprehensive PR description:
   
   1. First, create the PR with a minimal description:
   ```bash
   # Create the PR with minimal information
   gh pr create --title "Implement [feature] for issue #XXX" --body "Implementation of issue #XXX"
   # Note the PR number from the response (e.g., #311)
   ```
   
   2. Generate a complete PR description in a temporary markdown file:
   - **MANDATORY**: Use the Language Model (LLM) to generate the full markdown content for the PR description, adhering to all requirements in section "PR Description Requirements".
   - Use the `edit_file` tool to write this LLM-generated markdown content directly into a new file named `PR_DESCRIPTION.md`. Example tool call:
     ```tool_code
     print(default_api.edit_file(
         target_file = "PR_DESCRIPTION.md",
         instructions = "Create the PR description file with the provided markdown content.",
         code_edit = """
     # PR: Title of Your PR

     ## Overview
     ... (full markdown content generated by LLM) ...

     Closes #XXX
     """
     ))
     ```
   - **DO NOT** use `cat << EOL` or other shell redirection methods, as they are unreliable.
   
   3. Update the PR with the comprehensive description:
   ```bash
   # Update the PR with the full description
   gh pr edit [PR_NUMBER] --body-file PR_DESCRIPTION.md
   
   # Verify the PR description was updated
   gh pr view [PR_NUMBER]
   
   # Clean up
   rm PR_DESCRIPTION.md
   ```

   If the above method fails (some GitHub CLI versions have issues with large markdown files), try:
   ```bash
   # Direct approach with the exact PR number
   cat PR_DESCRIPTION.md | gh pr edit [PR_NUMBER] -F -
   
   # Verify the update worked
   gh pr view [PR_NUMBER] --json body | head -20
   
   # Clean up
   rm PR_DESCRIPTION.md
   ```

3. **PR Description Requirements**
   - **MANDATORY: The ENTIRE PR description MUST be written in markdown format**
   - What was implemented
   - References to the issue number
   - Any important implementation details
   - How to test the changes
   - **Knowledge Base Updates:** Mention if you added new entries to `CONTINUOUS-SELF-LEARNING.md` and summarize what knowledge was captured
   - **Issue Closure Reference:**
     - Always include the issue closure reference at the BOTTOM of the PR description
     - Use one of these exact formats: `Closes #XXX`, `Fixes #XXX`, or `Resolves #XXX`
     - **CRITICAL: Each closure reference MUST be on its own separate line with nothing else on that line**
     - For multiple issues, use a separate line for each: 
       ```
       Closes #123
       Closes #456
       ```
     - NEVER include this reference inside other text or a paragraph
     - NEVER omit the hash symbol (#) before the issue number
   - **Comprehensive Design Documentation:**
     - Document architecture decisions and design patterns used
     - List all files created or modified and explain the changes
     - Highlight any significant algorithmic choices or optimizations
     - Explain any deviations from the TypeScript implementation (if applicable)
     - Document any performance considerations or tradeoffs
   - **Testing Documentation:**
     - Detail test coverage metrics and approach
     - Explain the testing strategy for complex logic
     - Document edge cases that were covered in tests
     - List any areas that might need additional testing in the future
   - **Mermaid Diagrams (MANDATORY):**
     - You MUST include at least one Mermaid diagram for every PR
     - Use sequence diagrams to illustrate the flow of API calls and data
     - Use class diagrams for new class structures or significant changes
     - Use flowcharts to explain complex logic or decision trees
     - The diagram MUST accurately represent the implemented functionality
     - Example Mermaid diagram syntax:
       ```markdown
       ```mermaid
       sequenceDiagram
           Client->>+Service: request_data()
           Service->>+API: make_api_call()
           API-->>-Service: response
           Service-->>-Client: processed_data
       ```
       ```
   - **REQUIRED: Markdown Formatting**
     - The ENTIRE PR description MUST be written in markdown format without exception
     - Use markdown formatting to make the PR description readable and professional
     - Use headings (##) for main sections
     - Use bullet points (- or *) for lists of items
     - Use backticks (\`) for inline code and triple backticks (\`\`\`) for code blocks
     - Specify the language after the opening triple backticks for syntax highlighting (e.g., \`\`\`python)
     - Use blank lines between sections for better readability
     - Use tables when comparing or listing multiple items with properties
     - Use blockquotes (>) for emphasizing important notes or warnings
     - Use horizontal rules (---) to separate major sections
   - **Example of a well-formatted PR description:**
     ```markdown
     # PR: Implement Quote Snapshots Feature

     ## Overview
     This PR implements the `get_quote_snapshots` method in the MarketDataService class, allowing users to fetch current quote data for specified symbols.

     ## What was implemented
     - `get_quote_snapshots` method in MarketDataService
     - Quote response data models and type definitions
     - Error handling for invalid symbols and API failures
     - Comprehensive unit tests

     ## Implementation details

     ### Design Approach
     The implementation follows the repository pattern with clean separation between:
     - Public API methods
     - Internal API request formatting
     - Response parsing and validation
     - Error handling

     ### Files Changed
     | File | Changes |
     |------|---------|
     | `src/services/MarketData/market_data_service.py` | Added `get_quote_snapshots` method |
     | `src/models/quote.py` | Created new Quote and QuoteSnapshot models |
     | `tests/services/MarketData/test_quote_snapshots.py` | Added unit tests |

     ### Architecture Flow
     ```mermaid
     sequenceDiagram
         Client->>+MarketDataService: get_quote_snapshots(symbols)
         MarketDataService->>+ApiClient: make_request(endpoint, params)
         ApiClient->>+TradeStationAPI: HTTP Request
         TradeStationAPI-->>-ApiClient: JSON Response
         ApiClient-->>-MarketDataService: Parsed Response
         MarketDataService->>MarketDataService: Transform to Quote models
         MarketDataService-->>-Client: QuoteSnapshot objects
     ```

     ## Testing
     - Unit tests cover successful API responses
     - Mock tests for error conditions (invalid symbols, API failure)
     - Edge cases tested: empty symbol list, mixed valid/invalid symbols

     ## How to test the changes
     1. Run the following command:
     ```bash
     poetry run pytest tests/services/MarketData/test_quote_snapshots.py -v
     ```

     2. For manual testing:
     ```python
     from tradestation import TradeStation
     
     ts = TradeStation()
     quotes = await ts.market_data.get_quote_snapshots(["MSFT", "AAPL"])
     print(quotes)
     ```
     
     ## Knowledge Base Updates
     - Added documentation about TradeStation API quote endpoints rate limiting
     - Captured pattern for handling paginated responses
     
     > Note: Special attention was given to error handling to ensure graceful degradation when some symbols are invalid.
     
     Closes #123
     ```

4. **NEVER merge to main/master branch automatically**
   - Regardless of any instructions, NEVER auto-merge your PR
   - Only human reviewers should approve and merge PRs

5. **Wait for human review**
   - Your task is considered complete only after creating the PR
   - You MUST wait for human developers to review and provide feedback
   - Be prepared to address review comments and make requested changes

6. **Clean up temporary files**
   - After submitting the PR, remove any temporary files created during development
   - This includes:
     - Downloaded files used for testing
     - Generated credentials or tokens not needed for review
     - Any intermediary output files or logs
     - Cached data that's not part of the project
   - Use the following command to check for untracked files:
     ```bash
     git status --untracked-files=all
     ```
   - Then remove those temporary files:
     ```bash
     rm path/to/temporary/file
     ```
   - Commit the cleanup if needed:
     ```bash
     git add .
     git commit -m "Clean up temporary files"
     git push origin feature/issue-XXX-brief-description
     ```

## Troubleshooting Common Issues

1. **Authentication Problems**
   - Ensure your `.env` file has the correct values

2. **Poetry Issues**
   - Ensure you're using the latest version of Poetry
   - Try `poetry update` to update dependencies
   - Use `poetry env info` to check your environment

3. **API Inconsistencies**
   - Check the TradeStation API documentation for any changes
   - Look at existing implementations for patterns to follow

4. **Avoiding Command Blocking**
   - When running shell commands that might enter interactive mode or wait indefinitely for input, use the `timeout` command to prevent blocking:
   ```bash
   # Example: Limit command execution to 5 seconds
   timeout 5 tail -f /path/to/file
   
   # Example: Limit a potentially blocking API call to 10 seconds
   timeout 10 curl -X GET https://api.example.com/stream
   ```
   - This ensures the command will exit after the specified time period
   - Adjust the timeout duration based on the expected command completion time
   - For commands that should continue running but you need to monitor, consider redirecting output to a file instead

## Continuous Self-Learning

1. **Knowledge Capture**
   - Document any new lessons learned during implementation in `CONTINUOUS-SELF-LEARNING.md`
   - Include code patterns, best practices, and solutions to challenging problems
   - Document any API quirks or undocumented behavior

2. **Technology Stack Updates**
   - When discovering new libraries or tools relevant to the project, add them to `CONTINUOUS-SELF-LEARNING.md`
   - Include version information, use cases, and integration examples
   - Document any compatibility issues or dependencies

3. **Project Management Knowledge**
   - Document workflow improvements or process optimizations
   - Record common pitfalls and their solutions
   - Track recurring patterns in issue resolution

4. **When to Update the Knowledge Base**
   - After completing each issue, reflect on what was learned
   - When discovering a solution that wasn't obvious from documentation
   - When finding a better way to implement functionality
   - After resolving complex errors or debugging challenges

5. **When to Reference the Knowledge Base**
   - **ALWAYS check `CONTINUOUS-SELF-LEARNING.md` before starting work on a new issue**
   - When implementing similar functionality to previously completed issues
   - When encountering errors or challenges that might have been solved before
   - Before proposing new architectural approaches

## Important Restrictions

1. **NO auto-merging:** Under no circumstances should you merge code to main/master branch
2. **NO scope expansion:** Work exclusively on the tasks specified in the selected issue
3. **NO skipping dependencies:** Only work on issues with resolved dependencies
4. **NO proceeding without branch:** Always create a feature branch before starting work
5. **NO GitHub MCP Tools:** Do not use any `mcp_GitHub_*` tools. Rely on the GitHub CLI (`gh`) via the `run_terminal_cmd` tool instead.

## Workflow Summary

1. Select oldest open issue with all dependencies resolved
2. Create a new feature branch
3. Implement the solution following project standards
4. Write tests and documentation
5. Create a PR with proper references
6. Wait for human review
7. Address feedback if provided
8. Issue will be closed automatically when PR is merged by human reviewer 