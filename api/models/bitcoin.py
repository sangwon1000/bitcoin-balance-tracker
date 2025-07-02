"""
Bitcoin-related data models for the API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


class AddressRequest(BaseModel):
    """Single address request"""
    address: str = Field(..., description="Bitcoin address")
    
    @validator('address')
    def validate_address_format(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Address cannot be empty")
        return v.strip()


class MultipleAddressRequest(BaseModel):
    """Multiple addresses request"""
    addresses: List[str] = Field(..., min_items=1, max_items=50, description="List of Bitcoin addresses")
    
    @validator('addresses')
    def validate_addresses(cls, v):
        if not v:
            raise ValueError("At least one address required")
        cleaned = [addr.strip() for addr in v if addr.strip()]
        if not cleaned:
            raise ValueError("No valid addresses provided")
        return cleaned


class AddressBalance(BaseModel):
    """Address balance information"""
    address: str
    confirmed_balance: Decimal = Field(..., description="Confirmed balance in BTC")
    unconfirmed_balance: Decimal = Field(..., description="Unconfirmed balance in BTC")
    total_balance: Decimal = Field(..., description="Total balance in BTC")
    address_type: str = Field(..., description="Address type (P2PKH, P2SH, Bech32, etc.)")
    last_updated: str = Field(..., description="Last updated timestamp")


class TransactionHistoryRequest(BaseModel):
    """Transaction history request"""
    address: str = Field(..., description="Bitcoin address")
    limit: int = Field(10, ge=1, le=100, description="Number of transactions to return")
    offset: int = Field(0, ge=0, description="Number of transactions to skip")


class AddressHistory(BaseModel):
    """Address transaction history"""
    address: str
    transactions: List[Dict[str, Any]] = Field(..., description="List of transactions")
    total_transactions: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Transactions per page")


class ServerInfo(BaseModel):
    """Electrum server information"""
    server_host: str = Field(..., description="Server hostname")
    server_port: int = Field(..., description="Server port")
    protocol_version: Optional[str] = Field(None, description="Protocol version")
    server_version: Optional[str] = Field(None, description="Server version")
    genesis_hash: Optional[str] = Field(None, description="Genesis block hash")
    height: Optional[int] = Field(None, description="Current block height")
    connected: bool = Field(..., description="Connection status")
    last_ping: Optional[float] = Field(None, description="Last ping time")
    response_time: Optional[float] = Field(None, description="Average response time")


class DiscoverServersRequest(BaseModel):
    """Server discovery request"""
    max_servers: Optional[int] = Field(10, ge=1, le=50, description="Maximum servers to return")
    test_connection: bool = Field(True, description="Test server connections")


class ServerList(BaseModel):
    """List of discovered servers"""
    servers: List[Dict[str, Any]] = Field(..., description="List of servers")
    total_discovered: int = Field(..., description="Total servers discovered")
    health_checked: int = Field(..., description="Number of servers health checked")
    timestamp: str = Field(..., description="Discovery timestamp")


class AddressValidationRequest(BaseModel):
    """Address validation request"""
    address: str = Field(..., description="Bitcoin address to validate")


class AddressValidationResponse(BaseModel):
    """Address validation response"""
    address: str = Field(..., description="Original address")
    is_valid: bool = Field(..., description="Whether address is valid")
    address_type: Optional[str] = Field(None, description="Address type if valid")
    network: Optional[str] = Field(None, description="Network (mainnet/testnet)")
    error: Optional[str] = Field(None, description="Error message if invalid") 