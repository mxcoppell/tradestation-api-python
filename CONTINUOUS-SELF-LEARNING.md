# Agent Continuous Learning Knowledge Base

## Technical Patterns & Best Practices

### Python Implementation Patterns
- When implementing streaming functionality for market data, use `WebSocketStream` with callback pattern to handle asynchronous events. This allows easy processing of incoming data without blocking. **Correction:** This is no longer accurate for SSE streams.
- **New:** For HTTP-based Server-Sent Events (SSE) streams (like `/v3/marketdata/stream/quotes`), use the `HttpClient.create_stream` method which returns an `aiohttp.StreamReader`. Process the stream line-by-line, decoding bytes, and parsing JSON data.
- **New:** When creating scripts in the `examples/` directory that need to import project modules, use direct imports relative to the `src` directory (e.g., `from src.client import TradeStationClient`, `from src.ts_types.config import ApiError`). Avoid package-level imports (e.g., `from tradestation import ...`) or `sys.path` manipulation, as these may fail when running the script directly with `poetry run python examples/...`.

### API Integration Techniques
- TradeStation API uses Server-Sent Events (SSE) for **some** streaming data endpoints (e.g., quotes). **Correction:** Removed incorrect reference to `WebSocketStream` wrapping SSE.
- Streaming endpoints require the 'Accept: application/vnd.tradestation.streams.v2+json' header for proper data formatting. This header should be passed to `HttpClient.create_stream`.
- **New:** Use GitHub command line tool or `curl` with the raw file URL (e.g., `https://raw.githubusercontent.com/owner/repo/branch/path/to/file`) via the `run_terminal_cmd` tool to access GitHub repositories.

### Error Handling Strategies
- For streaming bar data, validate parameters before making API calls to prevent runtime errors.
- Key validations include:
  - Interval must be 1 for non-minute bars
  - Maximum interval for minute bars is 1440
  - Maximum of 57,600 historical bars allowed per request
- **New:** When processing SSE streams via `StreamReader`, handle potential `json.JSONDecodeError` for non-JSON lines (e.g., empty lines, potential metadata) and `asyncio.TimeoutError` if using `asyncio.wait_for` to allow graceful shutdown.
- **New:** The `aiohttp.ClientResponse.raise_for_status()` method is **not** awaitable and should be called synchronously.

### Pull Request Creation Strategy
- Generate comprehensive PR descriptions with these steps:
  1. Create the initial PR with a minimal description using GitHub CLI:
     ```bash
     gh pr create --title "PR title" --body "Implementation of issue #XXX"
     # Note the PR number from the response (e.g., #326)
     ```
  2. **MANDATORY**: Use the Language Model (LLM) to generate the full markdown content for the PR description adhering to all requirements in `AGENT-INSTRUCTION.md`.
  3. **MANDATORY**: Use the `edit_file` tool to write the LLM-generated markdown directly into a new file named `PR_DESCRIPTION.md`. Do not use `cat` or other shell commands.
  4. Update the PR with the full description using the file:
     ```bash
     gh pr edit <PR_NUMBER> --body-file PR_DESCRIPTION.md
     ```
  5. Verify the PR content:
     ```bash
     gh pr view <PR_NUMBER> | head -20
     ```
  6. Clean up the temporary file:
     ```bash
     rm PR_DESCRIPTION.md
     ```
- This workflow prevents issues with command length limitations in the terminal and ensures a properly formatted, comprehensive PR description is applied.
- **ALWAYS** follow this method for creating PR descriptions.

## Technology Stack Insights

### Core Libraries
- AsyncIO is essential for handling streaming data with proper concurrency.
- **New:** `aiohttp.StreamReader` is used for processing HTTP-based SSE streams returned by `HttpClient.create_stream`.
- WebSocketStream provides a consistent interface for all streaming endpoints **Correction:** This is likely only true for actual WebSocket endpoints, not SSE.

### Testing Tools
- Mock WebSocketStream and callbacks to test streaming functionality without real API calls **Correction:** For SSE streams, mock `HttpClient.create_stream` to return a mocked `aiohttp.StreamReader` and simulate its `readline` method.
- Use AsyncMock for testing async methods; MagicMock for non-async components.

### Useful Utilities
- TradeStation provides heartbeats every 5 seconds for detecting connection health on streaming endpoints.
- Properly handle 'Heartbeat', data, and error messages using conditional checks when processing stream data.

## Project Management Insights

### Workflow Optimizations
- Implement similar streaming endpoints using the same pattern: validate parameters, call `stream_manager.create_stream` (for WebSockets) or `http_client.create_stream` (for SSE), and document usage examples.

### Common Pitfalls
- Forgetting to handle different message types in streaming callbacks (data vs heartbeat vs error)
- Not validating parameters before making streaming API calls can lead to cryptic server errors
- Not cleaning up temporary files and directories created during development
- **New:** Assuming all TradeStation streaming endpoints use WebSockets; some use HTTP SSE.
- **New:** Using `await` on non-awaitable methods like `aiohttp.ClientResponse.raise_for_status()`.
- **New:** Incorrectly mocking SSE streams as WebSocket streams in tests.
- **New:** Using `gh issue view <id> --comments` to fetch issue details; this command only retrieves *comments* added after the initial description. Use `gh issue view <id>` to get the full issue description and subsequent comments.

### Issue Resolution Patterns
- For streaming implementations, follow the existing pattern of internal validation followed by `stream_manager.create_stream` call **or** `http_client.create_stream` depending on the underlying protocol (WebSocket vs SSE).

### Development Cleanliness
- Always remove temporary files and directories created during development (e.g., `temp/`, files for PR descriptions) before committing changes
- Use `git status --untracked-files=all` to check for untracked files that might need cleanup
- Keep the repository clean to prevent confusion for other developers and avoid accidental commits of temporary files

## API Behavior & Quirks

### TradeStation API Specifics
- Bar streaming endpoints can provide both historical and real-time data in the same stream.
- Bar streams include IsRealtime and IsEndOfHistory flags to distinguish between historical and real-time data.
- **New:** Quote streaming (`/v3/marketdata/stream/quotes/{symbols}`) uses HTTP SSE, not WebSockets.

### Authentication Nuances
- 

### Rate Limiting & Performance
- Bar streaming endpoint allows a maximum of 57,600 historical bars per request.
- For unit "Minute", the max allowed Interval is 1440 (representing 1 day).

