# Improved Error Handling and Exception Hierarchy

## Overview

This PR implements enhancements to the error handling system in the TradeStation API Python wrapper, addressing issue #364. The changes include documentation updates, improved exception handling in the client, and example code demonstrating best practices.

## Changes

1. **Fixed Bug in HTTP Client**:
   - Added missing `raise_for_status()` call in the `create_stream` method

2. **Documentation Enhancements**:
   - Added comprehensive error handling section to README.md
   - Created detailed `docs/error_handling.md` guide
   - Added exception information to method docstrings

3. **Example Code**:
   - Created `examples/QuickStart/error_handling.py` demonstrating:
     - Proper exception handling patterns
     - Retry logic with exponential backoff
     - Streaming error management
     - Resource cleanup in finally blocks

4. **TradeStation Client Updates**:
   - Enhanced docstrings with exception information
   - Improved error context in client methods

## Testing

All 338 tests are passing. The changes are backward compatible and maintain existing functionality.

## Documentation

The PR includes detailed documentation on:
- Exception hierarchy and when each exception is raised
- Best practices for error handling
- Retry patterns for transient errors
- Extracting useful information from exceptions

## Related Issue

Closes #364 