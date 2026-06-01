"""Solana RPC client for fetching wallet balances."""

import time
import logging
from typing import Optional, Dict, Any
from decimal import Decimal

from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed

from config import SolanaConfig


logger = logging.getLogger("solana_wallet_fetcher")

# Constants
LAMPORTS_PER_SOL = 1_000_000_000
MIN_WALLET_ADDRESS_LENGTH = 43
MAX_WALLET_ADDRESS_LENGTH = 44


class InvalidWalletAddressError(Exception):
    """Raised when wallet address format is invalid."""
    pass


class RPCConnectionError(Exception):
    """Raised when RPC connection fails."""
    pass


class WalletBalanceError(Exception):
    """Raised when unable to fetch wallet balance."""
    pass


class SolanaClient:
    """
    Production-ready Solana RPC client for fetching wallet balances.
    
    This class handles connection to Solana RPC nodes, validates wallet addresses,
    and retrieves wallet balances with comprehensive error handling.
    """
    
    def __init__(self, config: SolanaConfig) -> None:
        """
        Initialize Solana client with configuration.
        
        Args:
            config: SolanaConfig instance with RPC settings.
            
        Raises:
            RPCConnectionError: If unable to connect to RPC node.
        """
        self.config = config
        self.client: Optional[Client] = None
        self._connect()
    
    def _connect(self) -> None:
        """
        Establish connection to Solana RPC node with retry logic.
        
        Raises:
            RPCConnectionError: If connection fails after all retries.
        """
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                logger.info(
                    f"Attempting to connect to Solana RPC "
                    f"(attempt {attempt}/{self.config.max_retries})"
                )
                
                self.client = Client(
                    self.config.rpc_url,
                    timeout=self.config.request_timeout,
                )
                
                # Test connection by getting the RPC version
                response = self.client.get_version()
                
                # Check if response is valid (handles both dict and object responses)
                if response:
                    logger.info(
                        f"Successfully connected to Solana RPC. "
                        f"Version: {response}"
                    )
                    return
                else:
                    raise RPCConnectionError("Invalid RPC response")
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Connection attempt {attempt} failed: {str(e)}"
                )
                
                if attempt < self.config.max_retries:
                    wait_time = self.config.retry_delay * attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        error_message = (
            f"Failed to connect to Solana RPC after {self.config.max_retries} "
            f"attempts. Last error: {str(last_error)}"
        )
        logger.error(error_message)
        raise RPCConnectionError(error_message)
    
    def validate_wallet_address(self, address: str) -> bool:
        """
        Validate Solana wallet address format.
        
        Args:
            address: Wallet address to validate.
            
        Returns:
            bool: True if valid, False otherwise.
            
        Raises:
            InvalidWalletAddressError: If address is invalid.
        """
        if not address or not isinstance(address, str):
            raise InvalidWalletAddressError("Wallet address must be a non-empty string")
        
        address = address.strip()
        
        if len(address) < MIN_WALLET_ADDRESS_LENGTH or len(address) > MAX_WALLET_ADDRESS_LENGTH:
            raise InvalidWalletAddressError(
                f"Wallet address must be between {MIN_WALLET_ADDRESS_LENGTH} and "
                f"{MAX_WALLET_ADDRESS_LENGTH} characters long. Got {len(address)}"
            )
        
        try:
            Pubkey.from_string(address)
            logger.debug(f"Wallet address validated: {address}")
            return True
        except Exception as e:
            raise InvalidWalletAddressError(
                f"Invalid Solana wallet address format: {str(e)}"
            )
    
    def get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        Fetch wallet balance from Solana blockchain.
        
        Args:
            wallet_address: Solana wallet address in base58 format.
            
        Returns:
            Dictionary containing:
                - address: The wallet address
                - balance_lamports: Balance in lamports (int)
                - balance_sol: Balance in SOL (Decimal)
                - formatted_sol: Balance formatted to 9 decimal places (str)
                
        Raises:
            InvalidWalletAddressError: If wallet address is invalid.
            WalletBalanceError: If unable to fetch balance.
        """
        if not self.client:
            raise RPCConnectionError("Not connected to RPC node")
        
        # Validate wallet address
        self.validate_wallet_address(wallet_address)
        
        try:
            logger.info(f"Fetching balance for wallet: {wallet_address}")
            
            public_key = Pubkey.from_string(wallet_address)
            
            # Get balance with confirmed commitment level
            response = self.client.get_balance(
                public_key,
                commitment=Confirmed,
            )
            
            # Handle both dict and object responses
            if hasattr(response, 'value'):
                balance_lamports = response.value
            elif isinstance(response, dict) and "result" in response:
                balance_lamports = response["result"]["value"]
            else:
                raise WalletBalanceError(
                    f"Unable to retrieve balance for wallet {wallet_address}. "
                    "The wallet may not exist or RPC node is unavailable."
                )
            
            if balance_lamports is None:
                raise WalletBalanceError(
                    f"Unable to retrieve balance for wallet {wallet_address}. "
                    "The wallet may not exist or RPC node is unavailable."
                )
            
            balance_sol = self._lamports_to_sol(balance_lamports)
            formatted_sol = f"{float(balance_sol):.9f}".rstrip("0").rstrip(".")
            
            logger.info(
                f"Successfully fetched balance: {balance_lamports} lamports "
                f"({balance_sol} SOL)"
            )
            
            return {
                "address": wallet_address,
                "balance_lamports": balance_lamports,
                "balance_sol": balance_sol,
                "formatted_sol": formatted_sol,
            }
            
        except InvalidWalletAddressError:
            raise
        except Exception as e:
            error_message = f"Error fetching balance for {wallet_address}: {str(e)}"
            logger.error(error_message)
            raise WalletBalanceError(error_message)
    
    @staticmethod
    def _lamports_to_sol(lamports: int) -> Decimal:
        """
        Convert lamports to SOL.
        
        Args:
            lamports: Amount in lamports (smallest unit).
            
        Returns:
            Decimal: Amount in SOL.
        """
        return Decimal(lamports) / Decimal(LAMPORTS_PER_SOL)
    
    def close(self) -> None:
        """Close RPC connection gracefully."""
        if self.client:
            # The newer solana-py Client doesn't have a close method
            # but we keep this for API compatibility and future versions
            if hasattr(self.client, 'close'):
                logger.info("Closing Solana RPC connection")
                self.client.close()
            self.client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
