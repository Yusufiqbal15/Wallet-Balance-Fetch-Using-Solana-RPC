"""
Main entry point for Solana wallet balance fetcher.

This script demonstrates how to use the SolanaClient to fetch wallet balances
from the Solana blockchain.
"""

import sys
import logging
from typing import Optional

from config import get_config, logger
from solana_client import (
    SolanaClient,
    InvalidWalletAddressError,
    RPCConnectionError,
    WalletBalanceError,
)


def print_balance_report(wallet_address: str, balance_sol: str) -> None:
    """
    Print formatted wallet balance report.
    
    Args:
        wallet_address: The wallet address.
        balance_sol: The balance in SOL as a formatted string.
    """
    print("\n" + "=" * 50)
    print("Wallet Address:")
    print(wallet_address)
    print("\nBalance:")
    print(f"{balance_sol} SOL")
    print("=" * 50 + "\n")


def fetch_wallet_balance(wallet_address: str) -> Optional[str]:
    """
    Fetch and return wallet balance.
    
    Args:
        wallet_address: Solana wallet address.
        
    Returns:
        Balance in SOL as formatted string, or None if failed.
    """
    try:
        # Get configuration
        config = get_config()
        logger.debug("Configuration loaded successfully")
        
        # Initialize Solana client
        client = SolanaClient(config)
        
        try:
            # Fetch wallet balance
            balance_data = client.get_balance(wallet_address)
            
            return balance_data["formatted_sol"]
            
        finally:
            # Ensure connection is closed
            client.close()
            
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"\n❌ Configuration Error: {str(e)}")
        return None
        
    except InvalidWalletAddressError as e:
        logger.error(f"Invalid wallet address: {str(e)}")
        print(f"\n❌ Invalid Wallet Address: {str(e)}")
        return None
        
    except RPCConnectionError as e:
        logger.error(f"RPC connection error: {str(e)}")
        print(f"\n❌ RPC Connection Error: {str(e)}")
        print("Please check your RPC endpoint and network connectivity.")
        return None
        
    except WalletBalanceError as e:
        logger.error(f"Wallet balance error: {str(e)}")
        print(f"\n❌ Wallet Balance Error: {str(e)}")
        return None
        
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        print(f"\n❌ Unexpected Error: {str(e)}")
        return None


def main() -> int:
    """
    Main function to run wallet balance fetcher.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    logger.info("Starting Solana wallet balance fetcher")
    
    # Example wallet address (you can modify this or accept as command-line argument)
    # Using a known Solana wallet address for testing
    # In production, you would pass this as a command-line argument or configuration
    wallet_address = "FQvzfNddBRViBF6YBkZNwxA1kkHPW5v8DEjKKvWrCHSt"
    
    logger.info(f"Fetching balance for wallet: {wallet_address}")
    
    balance_sol = fetch_wallet_balance(wallet_address)
    
    if balance_sol is not None:
        print_balance_report(wallet_address, balance_sol)
        logger.info("Successfully completed wallet balance fetch")
        return 0
    else:
        logger.error("Failed to fetch wallet balance")
        return 1


if __name__ == "__main__":
    sys.exit(main())
