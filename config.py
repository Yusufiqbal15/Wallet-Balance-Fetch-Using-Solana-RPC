"""Configuration management for Solana wallet balance fetcher."""

import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


@dataclass
class SolanaConfig:
    """Configuration for Solana RPC client."""
    
    rpc_url: str
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.rpc_url:
            raise ValueError("RPC URL is required. Set SOLANA_RPC_URL in .env file")
        
        if not isinstance(self.rpc_url, str) or not self.rpc_url.strip():
            raise ValueError("RPC URL must be a non-empty string")
        
        if not self.rpc_url.startswith(("http://", "https://")):
            raise ValueError("RPC URL must start with http:// or https://")


def get_config() -> SolanaConfig:
    """
    Load and return Solana configuration from environment variables.
    
    Returns:
        SolanaConfig: Configuration object with RPC settings.
        
    Raises:
        ValueError: If required environment variables are missing.
    """
    rpc_url = os.getenv("SOLANA_RPC_URL")
    
    if not rpc_url:
        raise ValueError(
            "SOLANA_RPC_URL environment variable not set. "
            "Please configure it in your .env file."
        )
    
    request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay = float(os.getenv("RETRY_DELAY", "1.0"))
    
    return SolanaConfig(
        rpc_url=rpc_url,
        request_timeout=request_timeout,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("solana_wallet_fetcher")
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logging()
