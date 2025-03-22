# Authentication

The TradeStation API Python Wrapper uses OAuth 2.0 for authentication. This document explains how to authenticate with the TradeStation API using this library.

## TradeStation API Credentials

To use this library, you need to obtain TradeStation API credentials:

1. Log in to your TradeStation account
2. Navigate to the [Developer Portal](https://developer.tradestation.com/)
3. Create a new application to get your Client ID and Client Secret
4. Note your application's redirect URI

## Authentication Methods

The library supports several methods for providing authentication credentials:

### 1. Environment Variables

The simplest way to authenticate is to set your credentials as environment variables:

```bash
# Required
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REFRESH_TOKEN=your_refresh_token
ENVIRONMENT=Live  # or Simulation

# Optional
ACCESS_TOKEN=your_access_token  # Optional, will be obtained using refresh token if not provided
```

You can use a `.env` file for this purpose. The library includes a `.env.sample` file you can copy and modify.

### 2. Configuration Dictionary

You can pass configuration directly when creating the client:

```python
from src.client.tradestation_client import TradeStationClient

client = TradeStationClient({
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "refresh_token": "your_refresh_token",
    "environment": "Live"  # or "Simulation"
})
```

### 3. Direct Parameters

You can provide some parameters directly to the constructor:

```python
from src.client.tradestation_client import TradeStationClient

client = TradeStationClient(
    refresh_token="your_refresh_token",
    environment="Live"
)
```

When using this method, the client will still look for `CLIENT_ID` and `CLIENT_SECRET` in the environment variables.

## Obtaining a Refresh Token

To obtain a refresh token:

1. Register your application in the TradeStation Developer Portal
2. Set up your redirect URI (e.g., `http://localhost:8000/callback`)
3. Construct the authorization URL:

```
https://api.tradestation.com/v2/authorize?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  audience=https://api.tradestation.com&
  scope=openid offline_access profile MarketData ReadAccount Trade Matrix OptionSpreads&
  state=YOUR_STATE_VALUE
```

4. Navigate to this URL in a browser
5. Authorize your application
6. You'll be redirected to your redirect URI with a code parameter
7. Exchange this code for tokens:

```bash
curl -X POST https://api.tradestation.com/v2/security/authorize \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=YOUR_CODE" \
  -d "redirect_uri=YOUR_REDIRECT_URI"
```

8. From the response, save the `refresh_token` value

## Token Refreshing

The library automatically handles token refreshing. When an access token expires, the library will use the refresh token to obtain a new one. You don't need to manage this process manually.

## Getting the Current Refresh Token

You may need to retrieve the current refresh token (e.g., to save it for future sessions):

```python
refresh_token = client.get_refresh_token()
print(f"Current refresh token: {refresh_token}")
```

## Environments

TradeStation provides two environments:

- **Live**: Uses the production API at `https://api.tradestation.com`
- **Simulation**: Uses the simulator API at `https://sim.api.tradestation.com`

Specify the environment when creating the client:

```python
# Using environment variable
os.environ["ENVIRONMENT"] = "Simulation"

# Or in the configuration
client = TradeStationClient(environment="Simulation")
```

## Debug Mode

You can enable debug mode to see more information about the authentication process:

```python
client = TradeStationClient(debug=True)
```

This will print information about token refreshing, API requests, and other useful debugging details.

## Security Considerations

- Always keep your Client Secret and Refresh Token secure
- Do not commit these values to version control
- Use environment variables or a secure configuration manager in production
- Consider using a secrets management service for production deployments 