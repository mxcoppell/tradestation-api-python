# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-06-11

### Added
- Improved error handling system with a comprehensive exception hierarchy (closes #364)
- New exception classes for specific error types (authentication, rate limits, network, server errors)
- Helper functions for mapping HTTP status codes to appropriate exception types
- Error handling examples in examples/QuickStart/error_handling.py
- Detailed documentation on error handling in docs/error_handling.md

### Changed
- Updated method docstrings in TradeStationClient to include exception information
- Modified HTTP client to use the new exception system throughout all request methods

## [1.1.0] - 2025-06-09

### Fixed
- Restructured the project to follow standard Python packaging practices by moving all source code into the `src/tradestation` directory. This resolves import issues and allows users to import `TradeStationClient` and other components directly from the `tradestation` package (closes #362).
- Corrected all internal imports to be relative, ensuring the package works correctly when installed.

## [1.0.2] - 2025-04-21

### Changed
- Updated documentation links in README.md.

### Fixed
- Updated dependencies to the latest versions to resolve security vulnerabilities.
- Added support for Python 3.13.

## [1.0.1] - 2025-04-21

### Fixed
- Updated documentation links in README.md to point to GitHub repository.

## [1.0.0] - 2025-04-20

### Added
- Initial project setup.
- Core client structure.
- Authentication handling (`TokenManager`).
- Basic rate limiting (`RateLimiter`).
- Initial market data, brokerage, and order execution service placeholders.
- Foundational documentation (README, Quick Start, Authentication, Streaming, Rate Limiting, Contributing).
- Example scripts for Quick Start.
- Published to PyPI as `tradestation-api-python`. 