# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-01-08

### Security

- Updated urllib3 from 2.6.2 to 2.6.3 to fix high severity vulnerability:
  - CVE-2026-21441: High severity security vulnerability
- Updated filelock from 3.17.0 to 3.20.2 to fix medium severity vulnerability:
  - CVE-2025-68146: Medium severity security vulnerability
- Updated 28 additional dependencies to their latest versions for improved security and stability

## [1.3.0] - 2026-01-04

### Added

- Support for optional `client_secret` parameter to enable confidential OAuth clients (closes #366)
- `client_secret` can be provided via configuration dictionary or `CLIENT_SECRET` environment variable
- Documentation for public vs. confidential OAuth client types in authentication guide
- Clear distinction between public clients (no secret required) and confidential clients (secret required)

## [1.2.1] - 2026-01-03

### Security

- Updated urllib3 from 2.3.0 to 2.6.2 to fix multiple critical vulnerabilities:
  - CVE-2025-66418: Critical security vulnerability
  - CVE-2025-66471: Critical security vulnerability
  - CVE-2025-50181: Security vulnerability
  - CVE-2025-50182: Security vulnerability
- Updated aiohttp from 3.11.13 to 3.13.3 to fix high severity vulnerability:
  - CVE-2025-53643: High severity security vulnerability
- Updated requests from 2.32.3 to 2.32.5 to fix medium severity vulnerability:
  - CVE-2024-47081: Medium severity security vulnerability
- Updated black from 23.12.1 to 24.10.0 (dev dependency) to fix medium severity vulnerability:
  - CVE-2024-21503: Medium severity security vulnerability

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
