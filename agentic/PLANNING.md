# Planning

You are the project planner. This is the planning phase of this project. Read @PLANNING.md carefully.

- Make sure you have access to the GitHub typescript repository required in @PLANNING.md and can read the directory structure, code, tests, examples, and documents.
- Make sure you have full access to the python repository in @PLANNING.md  that has been created
- You must follow the order of the tasks defined in @PLANNING.md when creating issues. 
- You must only create issues for the tasks defined in  @PLANNING.md that has "[Task]" prefix.
- You must NOT change the task name defined in @PLANNING.mdwhen creating the issue for the task.
- For implementation tasks, you must understand the corresponding type script files to set the dependencies correctly in the issue to be created. 

Let me know if you have any questions before you start. 
You have GitHub command line tool with full access to both repositories. 
You must create issues for all the tasks defined in this document one by one.

The goal of this project is to create a Python clone of the "TradeStation API TypeScript Wrapper" (https://github.com/mxcoppell/tradestation-api-ts). You must study the Typescript repository to fully understand the project.

The GitHub repository for the Python clone is https://github.com/mxcoppell/tradestation-api-python.

# Project Directory Structure

We should mimic the directory struture of https://github.com/mxcoppell/tradestation-api-ts.

```
.
├── docs
├── examples
│   ├── Brokerage
│   ├── MarketData
│   ├── OrderExecution
│   └── QuickStart
└── src
    ├── client
    ├── services
    │       ├── Brokerage
    │       ├── MarketData
    │       └── OrderExecution
    ├── streaming
    ├── types
    └── utils
```

# Project Planning and Management

We are using GitHub to manage the progress of this project. 

The tasks are defined as the following [Task] items with the correct implemenation order. You must create individual GitHub issue for each Task in GitHub repository https://github.com/mxcoppell/tradestation-api-python. 

When creating each issue, you must study the TypeScript implementation to make sure to set the dependencies of each issue correctly.

Each issue to be created in GitHub repository must clearly state the following:
```
- The task detals to be completed
- The Typescript source files, test files, and/or documents that the task will clone from
- You must fully understand the Typescript implementation or document content. 
- You must faithfully and completely clone the Typescript version to Python version
- You must faithfully and completely clone the Typescript tests for the task to Python version
- You must not create tests for example codes or documents
- You must preserve all the comments for both the implementation and tests
- You must make sure the tests created for this task pass
- For the example you created, you must make sure example runs
- You must make sure the implementation of this task won't break any other tests in this project
- For each task, you must create a separate branch for the development and testing. And the completed branch must be merged back to the main/master branch to complete the task 
- Upon the completion of the task, you must update the task you worked on as completed/closed
```

## Setup project struct tasks
- [Task] Setup directory structure
- [Task] Setup dependency management (poetry)

## Development Tasks

### Types
- [Task] Create configuration types
- [Task] Create market data types
- [Task] Create brokerage types
- [Task] Create order exection types

### Utilities
- [Task] Create TokenManager
- [Task] Create RateLimiter
- [Task] Create StreamManager
- [Task] Create HttpClient
- [Task] Create TradeStation Client

### Services
Make sure you understand that in the source TypeScript project:
- src/services/MarketDataService.ts: for all market data functions
- src/services/BrokerageService.ts: for all brokerage functions
- src/services/OrderExecutionService.ts: for all order execution functions

So you can specify the source TypeScript file correctly in the Services issues.

#### Market Data Service
- [Task] Create Market Data Service: GetSymbolDetails
- [Task] Create Market Data Service: GetQuoteSnapshots
- [Task] Create Market Data Service: GetCryptoSymbolNames
- [Task] Create Market Data Service: GetOptionExpirations
- [Task] Create Market Data Service: GetBars
- [Task] Create Market Data Service: GetOptionRiskReward
- [Task] Create Market Data Service: GetOptionSpreadTypes
- [Task] Create Market Data Service: GetOptionStrikes
- [Task] Create Market Data Service: StreamBars
- [Task] Create Market Data Service: StreamMarketDepthAggregates
- [Task] Create Market Data Service: StreamMarketDepthQuotes
- [Task] Create Market Data Service: StreamOptionChain
- [Task] Create Market Data Service: StreamOptionQuotes
- [Task] Create Market Data Service: StreamQuotes

#### Brokerage Service
- [Task] Create Brokerage Service: GetAccounts
- [Task] Create Brokerage Service: GetBalances
- [Task] Create Brokerage Service: GetBalancesBOD
- [Task] Create Brokerage Service: GetHistoricalOrders
- [Task] Create Brokerage Service: GetHistoricalOrdersByOrderID
- [Task] Create Brokerage Service: GetOrders
- [Task] Create Brokerage Service: GetOrdersByOrderID
- [Task] Create Brokerage Service: GetPositions
- [Task] Create Brokerage Service: StreamOrders
- [Task] Create Brokerage Service: StreamOrdersByOrderID
- [Task] Create Brokerage Service: StreamPositions

#### Order Exection Service
- [Task] Create Order Execution Service: CancelOrder
- [Task] Create Order Execution Service: ConfirmGroupOrder
- [Task] Create Order Execution Service: ConfirmOrder
- [Task] Create Order Execution Service: GetActivationTriggers
- [Task] Create Order Execution Service: GetRoutes
- [Task] Create Order Execution Service: PlaceGroupOrder
- [Task] Create Order Execution Service: PlaceOrder
- [Task] Create Order Execution Service: ReplaceOrder

### Examples

#### Quick Start Example
- [Task] QuickStart Example: QuickStart

#### Market Data Examples
- [Task] Market Data Example: Get Symbol Details
- [Task] Market Data Example: Get Bars
- [Task] Market Data Example: Get Crypto Symbols
- [Task] Market Data Example: Get Option Expirations
- [Task] Market Data Example: Get Option RiskReward
- [Task] Market Data Example: Get Option SpreadTypes
- [Task] Market Data Example: Get Option Strikes
- [Task] Market Data Example: Get Quote Snapsh
- [Task] Market Data Example: Stream Bars
- [Task] Market Data Example: Stream Market Depth
- [Task] Market Data Example: Stream Market Depth Aggregates
- [Task] Market Data Example: Stream Option Chain
- [Task] Market Data Example: Stream Option Quotes
- [Task] Market Data Example: Stream Quotes

#### Brokerage Examples
- [Task] Brokerage Example: Get Accounts
- [Task] Brokerage Example: Get Balances
- [Task] Brokerage Example: Get Balances BOD
- [Task] Brokerage Example: Get Historical Orders
- [Task] Brokerage Example: Get Order By IDs
- [Task] Brokerage Example: Get Orders
- [Task] Brokerage Example: Get Positions
- [Task] Brokerage Example: Stream Orders
- [Task] Brokerage Example: Stream Positions

#### Order Execution Examples
- [Task] Order Execution Example: Confirm Group Order
- [Task] Order Execution Example: Confirm Order
- [Task] Order Execution Example: Get Activation Triggers
- [Task] Order Execution Example: Get Routes
- [Task] Order Execution Example: Place Cancel Order
- [Task] Order Execution Example: Place Group Order
- [Task] Order Execution Example: Replace Order

### Documents
- [Task] Document: API
- [Task] Document: Authentication
- [Task] Document: Examples
- [Task] Document: Quick Start
- [Task] Document: Rate Limiting
- [Task] Document: Streaming
- [Task] Document: README
- [Task] Document: CHANGELOG
- [Task] Document: CONTRIBUTING
- [Task] Document: LICENSE

### Publish Preparation
- [Task] Python Package Index (PyPI) publishing readiness

# Implementation Guidance For the Implementation Agents

You need to write an implementation guidance document in MD format under ./plan folder to guide the implementation agent how to pick up next open issue from the GitHub repository and complete the issue. 

Notice that we are using poetry as the dependency management tool. 

The purpose for this guide is to instruct the agent how to pick the next open issue by understanding the issue dependencies and complete the issue. 