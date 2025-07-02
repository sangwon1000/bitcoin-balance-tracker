"""
Bitcoin API endpoints - Simplified for single-user
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any
import logging
from decimal import Decimal
from datetime import datetime

from api.models.bitcoin import (
    AddressRequest, MultipleAddressRequest, AddressBalance,
    TransactionHistoryRequest, AddressHistory, ServerInfo,
    DiscoverServersRequest, ServerList, AddressValidationRequest,
    AddressValidationResponse
)
from api.models.responses import SuccessResponse
from api.core.auth import require_api_key
from bitcoin_tracker import BitcoinTracker

logger = logging.getLogger(__name__)
router = APIRouter()


def get_bitcoin_tracker(request: Request) -> BitcoinTracker:
    """Get Bitcoin tracker instance from app state"""
    return request.app.state.bitcoin_tracker


@router.get(
    "/balance/{address}",
    response_model=SuccessResponse,
    summary="Get Bitcoin address balance",
    description="Get the current balance for a specific Bitcoin address"
)
async def get_address_balance(
    address: str,
    request: Request,
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Get balance for a specific Bitcoin address"""
    try:
        # Validate address format
        if not bitcoin_tracker.validate_address(address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Bitcoin address format"
            )
        
        # Get balance
        balance_data = bitcoin_tracker.get_balance(address)
        
        if not balance_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found or unable to fetch balance"
            )
        
        # Format response
        address_balance = AddressBalance(
            address=address,
            confirmed_balance=Decimal(str(balance_data.get('confirmed', '0'))),
            unconfirmed_balance=Decimal(str(balance_data.get('unconfirmed', '0'))),
            total_balance=Decimal(str(balance_data.get('total', '0'))),
            address_type=balance_data.get('address_type', 'unknown'),
            last_updated=datetime.utcnow().isoformat()
        )
        
        return SuccessResponse(
            message="Balance retrieved successfully",
            data=address_balance
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get balance for {address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve balance"
        )


@router.post(
    "/balances",
    response_model=SuccessResponse,
    summary="Get multiple address balances",
    description="Get balances for multiple Bitcoin addresses in a single request"
)
async def get_multiple_balances(
    request_data: MultipleAddressRequest,
    request: Request,
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Get balances for multiple addresses"""
    try:
        balances = []
        
        for address in request_data.addresses:
            try:
                balance_data = bitcoin_tracker.get_balance(address)
                if balance_data:
                    address_balance = AddressBalance(
                        address=address,
                        confirmed_balance=Decimal(str(balance_data.get('confirmed', '0'))),
                        unconfirmed_balance=Decimal(str(balance_data.get('unconfirmed', '0'))),
                        total_balance=Decimal(str(balance_data.get('total', '0'))),
                        address_type=balance_data.get('address_type', 'unknown'),
                        last_updated=datetime.utcnow().isoformat()
                    )
                    balances.append(address_balance)
            except Exception as e:
                logger.warning(f"Failed to get balance for {address}: {e}")
                continue
        
        return SuccessResponse(
            message=f"Retrieved balances for {len(balances)} addresses",
            data=balances
        )
        
    except Exception as e:
        logger.error(f"Failed to get multiple balances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve balances"
        )


@router.get(
    "/history/{address}",
    response_model=SuccessResponse,
    summary="Get address transaction history",
    description="Get transaction history for a Bitcoin address"
)
async def get_address_history(
    address: str,
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Get transaction history for an address"""
    try:
        # Validate address
        if not bitcoin_tracker.validate_address(address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Bitcoin address format"
            )
        
        # Get transaction history
        history_data = bitcoin_tracker.get_transaction_history(address)
        
        if not history_data:
            return SuccessResponse(
                message="No transaction history found",
                data=AddressHistory(
                    address=address,
                    transactions=[],
                    total_transactions=0,
                    page=1,
                    per_page=limit
                )
            )
        
        # Apply pagination
        total_transactions = len(history_data)
        paginated_transactions = history_data[offset:offset + limit]
        
        # Format transactions
        formatted_transactions = []
        for tx in paginated_transactions:
            formatted_tx = {
                "txid": tx.get("tx_hash", ""),
                "confirmations": tx.get("confirmations", 0),
                "block_height": tx.get("height"),
                "timestamp": tx.get("timestamp"),
                "value": Decimal(str(tx.get("value", "0"))),
                "fee": Decimal(str(tx.get("fee", "0"))) if tx.get("fee") else None,
                "size": tx.get("size"),
                "inputs": tx.get("inputs", []),
                "outputs": tx.get("outputs", [])
            }
            formatted_transactions.append(formatted_tx)
        
        address_history = AddressHistory(
            address=address,
            transactions=formatted_transactions,
            total_transactions=total_transactions,
            page=(offset // limit) + 1,
            per_page=limit
        )
        
        return SuccessResponse(
            message="Transaction history retrieved successfully",
            data=address_history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get history for {address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )


@router.post(
    "/validate",
    response_model=SuccessResponse,
    summary="Validate Bitcoin address",
    description="Validate a Bitcoin address format and get its type"
)
async def validate_address(
    request_data: AddressValidationRequest,
    request: Request,
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Validate a Bitcoin address"""
    try:
        address = request_data.address
        is_valid = bitcoin_tracker.validate_address(address)
        
        response_data = AddressValidationResponse(
            address=address,
            is_valid=is_valid
        )
        
        if is_valid:
            try:
                address_type = bitcoin_tracker.get_address_type(address)
                response_data.address_type = address_type
                response_data.network = "mainnet"
            except Exception as e:
                logger.warning(f"Could not determine address type for {address}: {e}")
        else:
            response_data.error = "Invalid Bitcoin address format"
        
        return SuccessResponse(
            message="Address validation completed",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Address validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Address validation failed"
        )


@router.get(
    "/server-info",
    response_model=SuccessResponse,
    summary="Get Electrum server information",
    description="Get information about the currently connected Electrum server"
)
async def get_server_info(
    request: Request,
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Get current Electrum server information"""
    try:
        server_info_data = bitcoin_tracker.get_server_info()
        
        if not server_info_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No Electrum server connection available"
            )
        
        server_info = ServerInfo(
            server_host=server_info_data.get('host', 'unknown'),
            server_port=server_info_data.get('port', 0),
            protocol_version=server_info_data.get('protocol_version'),
            server_version=server_info_data.get('server_version'),
            genesis_hash=server_info_data.get('genesis_hash'),
            height=server_info_data.get('height'),
            connected=server_info_data.get('connected', False),
            last_ping=server_info_data.get('last_ping'),
            response_time=server_info_data.get('response_time')
        )
        
        return SuccessResponse(
            message="Server information retrieved successfully",
            data=server_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get server info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve server information"
        )


@router.post(
    "/discover-servers",
    response_model=SuccessResponse,
    summary="Discover Electrum servers",
    description="Discover and test Electrum servers for optimal performance"
)
async def discover_servers(
    request_data: DiscoverServersRequest,
    request: Request,
    authenticated: bool = require_api_key,
    bitcoin_tracker: BitcoinTracker = Depends(get_bitcoin_tracker)
):
    """Discover and test Electrum servers"""
    try:
        discovered_servers = bitcoin_tracker.discover_servers()
        
        if not discovered_servers:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No healthy Electrum servers found"
            )
        
        # Limit to requested maximum
        if request_data.max_servers:
            discovered_servers = discovered_servers[:request_data.max_servers]
        
        server_list = ServerList(
            servers=discovered_servers,
            total_discovered=len(discovered_servers),
            health_checked=len(discovered_servers),
            timestamp=datetime.utcnow().isoformat()
        )
        
        return SuccessResponse(
            message=f"Discovered {len(discovered_servers)} healthy servers",
            data=server_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Server discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server discovery failed"
        ) 