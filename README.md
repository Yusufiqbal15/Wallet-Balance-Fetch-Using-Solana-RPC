# Solana Wallet Balance Fetcher

A production-ready Python application for fetching Solana wallet balances using the Solana RPC API.

## Features

✅ **Production-Grade Architecture**
- Modular design with separate concerns (config, client, main)
- Reusable `SolanaClient` class for RPC interactions
- Context manager support for resource management

✅ **Robust Error Handling**
- Invalid wallet address validation
- RPC connection failure recovery with automatic retries
- Timeout error handling
- API response validation
- Comprehensive exception types

✅ **Security Best Practices**
- RPC URL stored in `.env` file (never hardcoded)
- Environment variable configuration via `python-dotenv`
- Secure secret management

✅ **Developer Experience**
- Full type hints for better IDE support
- Comprehensive logging at each step
- Detailed docstrings for all classes and methods
- Clear error messages for debugging

✅ **Performance**
- Configurable request timeout
- Automatic retry with exponential backoff
- Connection pooling support

## Installation

### Prerequisites
- Python 3.12+
- pip (Python package manager)

### Setup Steps

1. **Clone or create the project directory**
   ```bash
   cd /path/to/project
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - The `.env` file is already configured with the provided RPC endpoint
   - You can modify it to use a different RPC endpoint if needed

## Configuration

### Environment Variables (.env file)

```env
# Required: Solana RPC endpoint
SOLANA_RPC_URL=https://your-rpc-endpoint.com

# Optional: RPC client configuration
REQUEST_TIMEOUT=30              # Request timeout in seconds
MAX_RETRIES=3                   # Number of retry attempts
RETRY_DELAY=1.0                 # Initial retry delay in seconds
```

## Usage

### Basic Usage

Run the application with the default wallet address:

```bash
python main.py
```

### Output Example

```
==================================================
Wallet Address:
FQvzfNddBRViBF6YBkZNwxA1kkHPW5v8DEjKKvWrCHSt

Balance:
12.345678 SOL
==================================================
```

### Using as a Library

```python
from config import get_config
from solana_client import SolanaClient

# Get configuration
config = get_config()

# Initialize client
client = SolanaClient(config)

try:
    # Fetch balance
    balance_data = client.get_balance("FQvzfNddBRViBF6YBkZNwxA1kkHPW5v8DEjKKvWrCHSt")
    
    print(f"Balance: {balance_data['formatted_sol']} SOL")
    print(f"Lamports: {balance_data['balance_lamports']}")
    
finally:
    client.close()
```

### Using Context Manager

```python
from config import get_config
from solana_client import SolanaClient

config = get_config()

with SolanaClient(config) as client:
    balance_data = client.get_balance("FQvzfNddBRViBF6YBkZNwxA1kkHPW5v8DEjKKvWrCHSt")
    print(f"Balance: {balance_data['formatted_sol']} SOL")
```

## Project Structure

```
Wallet-Balance-Fetch-Using-Solana-RPC/
├── main.py                 # Entry point with example usage
├── config.py               # Configuration management
├── solana_client.py        # Solana RPC client class
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
└── README.md              # This file
```

### File Descriptions

#### `main.py`
- Main entry point for the application
- Demonstrates how to use the `SolanaClient`
- Includes error handling and formatted output
- Can be extended for command-line arguments

#### `config.py`
- Loads environment variables from `.env` file
- Defines `SolanaConfig` dataclass with validation
- Sets up logging configuration
- Provides `get_config()` function

#### `solana_client.py`
- Implements the `SolanaClient` class
- Handles RPC connection with retry logic
- Validates wallet addresses
- Fetches wallet balances
- Converts lamports to SOL
- Custom exception types for specific error scenarios

## Error Handling

The application handles the following error scenarios:

### `InvalidWalletAddressError`
- Raised when wallet address format is invalid
- Checks address length and base58 encoding
- Example: `SyntaxError: Invalid address length`

### `RPCConnectionError`
- Raised when unable to connect to RPC node
- Includes automatic retry with exponential backoff
- Example: `Connection timeout to RPC endpoint`

### `WalletBalanceError`
- Raised when unable to fetch wallet balance
- May indicate wallet doesn't exist or RPC issues
- Example: `Unable to retrieve balance for wallet`

### Logging

All operations are logged at appropriate levels:
- **INFO**: Connection status, balance retrieval, completion
- **DEBUG**: Validation steps, request details
- **WARNING**: Retry attempts, connection issues
- **ERROR**: All errors with context

View logs in the console output during execution.

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `solana-py` | 0.24.0 | Solana blockchain SDK |
| `solders` | 0.19.1 | Type definitions and serialization |
| `python-dotenv` | 1.0.0 | Environment variable management |

### Python Version
- **Required**: Python 3.12+
- **Tested**: Python 3.12

## API Reference

### SolanaClient

#### Constructor
```python
SolanaClient(config: SolanaConfig)
```
- Initializes client and connects to RPC node
- Raises: `RPCConnectionError` if connection fails

#### Methods

##### `get_balance(wallet_address: str) -> Dict`
Fetch wallet balance from blockchain.

**Parameters:**
- `wallet_address` (str): Solana wallet address in base58 format

**Returns:**
```python
{
    "address": str,              # Wallet address
    "balance_lamports": int,     # Balance in lamports
    "balance_sol": Decimal,      # Balance as Decimal
    "formatted_sol": str,        # Formatted balance string
}
```

**Raises:**
- `InvalidWalletAddressError`: Invalid address format
- `WalletBalanceError`: Failed to fetch balance

##### `validate_wallet_address(address: str) -> bool`
Validate wallet address format.

**Parameters:**
- `address` (str): Wallet address to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `InvalidWalletAddressError`: Invalid address

##### `close()`
Close RPC connection gracefully.

### SolanaConfig

Configuration dataclass with validation.

**Properties:**
- `rpc_url` (str): RPC endpoint URL
- `request_timeout` (int): Request timeout in seconds (default: 30)
- `max_retries` (int): Max retry attempts (default: 3)
- `retry_delay` (float): Initial retry delay in seconds (default: 1.0)

## Testing

### Test with Known Wallet

The default wallet in `main.py` is:
```
FQvzfNddBRViBF6YBkZNwxA1kkHPW5v8DEjKKvWrCHSt
```

This is a known active wallet on Solana mainnet.

### Custom Testing

Modify the `wallet_address` variable in `main.py`:

```python
wallet_address = "YOUR_WALLET_ADDRESS_HERE"
```

## Troubleshooting

### Issue: `SOLANA_RPC_URL environment variable not set`
**Solution**: Ensure `.env` file exists in the project root with `SOLANA_RPC_URL` defined.

### Issue: `Failed to connect to Solana RPC`
**Solution**: 
- Check your RPC endpoint is valid
- Verify internet connectivity
- Check RPC rate limits haven't been exceeded
- Try a different RPC endpoint

### Issue: `Invalid Solana wallet address format`
**Solution**:
- Verify wallet address is in base58 format
- Check address length (should be 43-44 characters)
- Copy address carefully (no extra spaces)

### Issue: Timeout errors
**Solution**:
- Increase `REQUEST_TIMEOUT` in `.env` file
- Check your network connection
- Try using a different RPC endpoint

## Performance Considerations

- **Latency**: First request may take longer due to connection establishment
- **Rate Limiting**: QuikNode may have rate limits; check your plan
- **Retry Logic**: Exponential backoff helps avoid overwhelming the RPC node
- **Timeout**: Adjust `REQUEST_TIMEOUT` based on your network conditions

## Security Considerations

✅ **Implemented**
- RPC URL in environment variables (not hardcoded)
- No credentials logged
- Input validation
- Exception handling (no sensitive data exposure)

⚠️ **Additional Recommendations for Production**
- Use a secure secrets manager (e.g., HashiCorp Vault, AWS Secrets Manager)
- Implement API key rotation
- Monitor RPC usage for anomalies
- Use VPN/proxy for RPC calls in sensitive environments
- Implement rate limiting on your application
- Add request signing for write operations (if extended)

## Extending the Application

### Add SPL Token Balance Support
```python
def get_token_balance(self, wallet: str, token_mint: str) -> str:
    """Fetch SPL token balance."""
    # Implementation here
```

### Add Price Conversion
```python
def get_sol_price(self) -> float:
    """Fetch SOL price in USD."""
    # Use CoinGecko or similar API
```

### Add Multiple Wallet Support
```python
def get_multiple_balances(self, addresses: List[str]) -> List[Dict]:
    """Fetch balances for multiple wallets."""
    # Implementation here
```

### Add Database Storage
```python
def store_balance_history(self, address: str, balance: float):
    """Store balance history in database."""
    # Implementation here
```

## Contributing

To contribute improvements:
1. Maintain Python 3.12 compatibility
2. Follow PEP 8 style guidelines
3. Add type hints to all functions
4. Include comprehensive docstrings
5. Handle errors appropriately
6. Update tests and documentation

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error messages in the logging output
3. Verify your `.env` configuration
4. Test with the known wallet address provided

## Resources

- [Solana Documentation](https://docs.solana.com/)
- [Solana Python SDK](https://github.com/michaelhly/solana-py)
- [Solana RPC API Reference](https://docs.solana.com/api/http)
- [QuikNode Documentation](https://www.quiknode.io/docs)

---

**Version**: 1.0.0  
**Last Updated**: June 2026  
**Python Version**: 3.12+
