# Agent Continuous Learning Knowledge Base

## Technical Patterns & Best Practices

### Python Implementation Patterns
- When implementing streaming functionality for market data, use `WebSocketStream` with callback pattern to handle asynchronous events. This allows easy processing of incoming data without blocking.

### API Integration Techniques
- TradeStation API uses Server-Sent Events (SSE) for streaming data, which is wrapped in our `WebSocketStream` implementation.
- Streaming endpoints require the 'Accept: application/vnd.tradestation.streams.v2+json' header for proper data formatting.

### Error Handling Strategies
- For streaming bar data, validate parameters before making API calls to prevent runtime errors.
- Key validations include:
  - Interval must be 1 for non-minute bars
  - Maximum interval for minute bars is 1440
  - Maximum of 57,600 historical bars allowed per request

### Pull Request Creation Strategy
- Create comprehensive PR descriptions with these steps:
  1. Create a local markdown file for the PR description (e.g., `touch PR_DESCRIPTION.md`)
  2. Edit the file with all required sections:
     - Overview
     - Features implemented
     - Implementation details (design approach, files changed)
     - Mermaid diagram for architecture flow
     - Testing strategy
     - Instructions for manual testing
     - Issue closure reference at the bottom (e.g., `Closes #XXX`)
  3. Create the initial PR with a minimal description: `gh pr create --title "PR title" --body "Implementation of issue #XXX"`
  4. Update the PR with the full description: `gh pr edit <PR_NUMBER> --body-file PR_DESCRIPTION.md`
  5. Verify the PR content: `gh pr view <PR_NUMBER>`
  6. Clean up temporary files: `rm PR_DESCRIPTION.md`
- This workflow prevents issues with the GitHub CLI command length limitations and ensures a properly formatted PR description.

## Technology Stack Insights

### Core Libraries
- AsyncIO is essential for handling streaming data with proper concurrency
- WebSocketStream provides a consistent interface for all streaming endpoints

### Testing Tools
- Mock WebSocketStream and callbacks to test streaming functionality without real API calls
- Use AsyncMock for testing async methods; MagicMock for non-async components

### Useful Utilities
- TradeStation provides heartbeats every 5 seconds for detecting connection health
- Properly handle 'Heartbeat', data, and error messages using conditional checks

## Project Management Insights

### Workflow Optimizations
- Implement similar streaming endpoints using the same pattern: validate parameters, call stream_manager.create_stream, and document usage examples

### Common Pitfalls
- Forgetting to handle different message types in streaming callbacks (data vs heartbeat vs error)
- Not validating parameters before making streaming API calls can lead to cryptic server errors
- Not cleaning up temporary files and directories created during development

### Issue Resolution Patterns
- For streaming implementations, follow the existing pattern of internal validation followed by stream_manager.create_stream call

### Development Cleanliness
- Always remove temporary files and directories created during development (e.g., `temp/`, files for PR descriptions) before committing changes
- Use `git status --untracked-files=all` to check for untracked files that might need cleanup
- Keep the repository clean to prevent confusion for other developers and avoid accidental commits of temporary files

## API Behavior & Quirks

### TradeStation API Specifics
- Bar streaming endpoints can provide both historical and real-time data in the same stream
- Bar streams include IsRealtime and IsEndOfHistory flags to distinguish between historical and real-time data

### Authentication Nuances
- 

### Rate Limiting & Performance
- Bar streaming endpoint allows a maximum of 57,600 historical bars per request
- For unit "Minute", the max allowed Interval is 1440 (representing 1 day)

