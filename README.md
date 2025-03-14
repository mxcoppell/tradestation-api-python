# TradeStation API Python Wrapper

A Python client library for the TradeStation API. This library provides a Pythonic interface to interact with TradeStation's API, allowing developers to easily integrate trading applications with TradeStation.

## Directory Structure

```
.
├── docs
├── examples
│   ├── Brokerage
│   ├── MarketData
│   ├── OrderExecution
│   └── QuickStart
└── src
    ├── client
    ├── services
    │       ├── Brokerage
    │       ├── MarketData
    │       └── OrderExecution
    ├── streaming
    ├── types
    └── utils
```

## Features

- Authentication workflow support
- Market Data services
- Brokerage services
- Order Execution services
- Streaming capabilities
- Rate limiting

## Requirements

- Python 3.11+
- TradeStation account
- TradeStation API keys

## Installation

```bash
# Install with Poetry
poetry install
```

## Quick Start

See the examples in the `examples/QuickStart` directory to get started.

## Documentation

Detailed documentation is available in the `docs` directory.

## License

MIT 