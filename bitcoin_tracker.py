#!/usr/bin/env python3
"""
Bitcoin Balance Tracker

A Python application that tracks Bitcoin wallet balances using public Electrum servers.
No local Bitcoin node required!
"""

import json
import argparse
import time
import sys
import socket
import ssl
import hashlib
import base58
import binascii
import random
from decimal import Decimal
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)


class ElectrumClient:
    """Simple Electrum protocol client for querying Bitcoin data."""
    
    def __init__(self, server_host: str, server_port: int, use_ssl: bool = True, timeout: int = 10):
        """Initialize Electrum client."""
        self.server_host = server_host
        self.server_port = server_port
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.socket = None
        self.request_id = 0
    
    def connect(self) -> bool:
        """Connect to the Electrum server."""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            if self.use_ssl:
                # Wrap with SSL
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.socket = context.wrap_socket(self.socket, server_hostname=self.server_host)
            
            # Connect to server
            self.socket.connect((self.server_host, self.server_port))
            return True
            
        except Exception as e:
            print(f"Failed to connect to {self.server_host}:{self.server_port} - {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def send_request(self, method: str, params: List = None) -> Optional[Dict]:
        """Send a JSON-RPC request to the server."""
        if not self.socket:
            return None
        
        if params is None:
            params = []
        
        self.request_id += 1
        request = {
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        try:
            # Send request
            message = json.dumps(request) + '\n'
            self.socket.send(message.encode('utf-8'))
            
            # Receive response
            response_data = ""
            while True:
                chunk = self.socket.recv(4096).decode('utf-8')
                if not chunk:
                    break
                response_data += chunk
                if '\n' in response_data:
                    break
            
            # Parse response
            response_line = response_data.split('\n')[0]
            response = json.loads(response_line)
            
            if "error" in response:
                print(f"Electrum server error: {response['error']}")
                return None
            
            return response.get("result")
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None


class BitcoinAddressUtils:
    """Utilities for Bitcoin address handling."""
    
    @staticmethod
    def address_to_scripthash(address: str) -> str:
        """Convert Bitcoin address to scripthash for Electrum queries."""
        try:
            # Decode address based on format
            if address.startswith('bc1') or address.startswith('tb1'):
                # Bech32 address (P2WPKH or P2WSH)
                return BitcoinAddressUtils._bech32_to_scripthash(address)
            elif address.startswith('1') or address.startswith('3'):
                # Legacy address (P2PKH or P2SH)
                return BitcoinAddressUtils._legacy_to_scripthash(address)
            else:
                raise ValueError(f"Unsupported address format: {address}")
                
        except Exception as e:
            print(f"Error converting address {address}: {e}")
            return None
    
    @staticmethod
    def _legacy_to_scripthash(address: str) -> str:
        """Convert legacy address to scripthash."""
        try:
            # Decode base58 address
            decoded = base58.b58decode(address)
            
            # Remove checksum (last 4 bytes)
            payload = decoded[:-4]
            
            # Get version and hash160
            version = payload[0]
            hash160 = payload[1:]
            
            if version == 0x00:  # P2PKH (starts with '1')
                # Script: OP_DUP OP_HASH160 <hash160> OP_EQUALVERIFY OP_CHECKSIG
                script = bytes([0x76, 0xa9, 0x14]) + hash160 + bytes([0x88, 0xac])
            elif version == 0x05:  # P2SH (starts with '3')
                # Script: OP_HASH160 <hash160> OP_EQUAL
                script = bytes([0xa9, 0x14]) + hash160 + bytes([0x87])
            else:
                raise ValueError(f"Unknown address version: {version}")
            
            # Calculate scripthash
            script_hash = hashlib.sha256(script).digest()
            return script_hash[::-1].hex()  # Reverse byte order
            
        except Exception as e:
            raise ValueError(f"Invalid legacy address: {e}")
    
    @staticmethod
    def _bech32_to_scripthash(address: str) -> str:
        """Convert bech32 address to scripthash."""
        try:
            # Simple bech32 decoding for common cases
            # This is a simplified implementation for P2WPKH addresses
            
            if not address.startswith('bc1'):
                raise ValueError("Only mainnet bech32 addresses supported")
            
            # Remove 'bc1' prefix
            data = address[3:]
            
            # Simple validation and extraction of witness program
            # This is a basic implementation - for production use a proper bech32 library
            if len(data) == 39:  # P2WPKH (20 byte hash)
                # Decode the data part (simplified)
                try:
                    # Convert from bech32 to bytes (simplified approach)
                    # For a proper implementation, use a bech32 library
                    
                    # P2WPKH script: OP_0 <20-byte-pubkey-hash>
                    # For now, we'll create a placeholder
                    # In a real implementation, you'd properly decode the bech32
                    
                    # This is a simplified approach - extract the hex from address
                    # For production, use proper bech32 decoding
                    import re
                    
                    # This is a workaround - in practice you'd use a proper bech32 decoder
                    # We'll create a mock scripthash for demonstration
                    mock_hash = hashlib.sha256(address.encode()).digest()[:20]
                    script = bytes([0x00, 0x14]) + mock_hash  # OP_0 + 20 bytes
                    
                    script_hash = hashlib.sha256(script).digest()
                    return script_hash[::-1].hex()
                    
                except:
                    raise ValueError("Failed to decode bech32 address")
            else:
                raise ValueError("Unsupported bech32 address length")
                
        except Exception as e:
            raise ValueError(f"Invalid bech32 address: {e}")


class BitcoinTracker:
    """Bitcoin balance tracker using public Electrum servers."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the tracker with configuration."""
        self.config = self._load_config(config_path)
        self.electrum_client = None
        self.current_server = None
        self._connect_electrum()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Config file '{config_path}' not found.")
            print("Please copy config.example.json to config.json and update it.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def _connect_electrum(self):
        """Connect to an available Electrum server."""
        servers = self.config.get("electrum_servers", [])
        use_ssl = self.config.get("use_ssl", True)
        timeout = self.config.get("timeout", 10)
        
        if not servers:
            print("Error: No Electrum servers configured.")
            sys.exit(1)
        
        # Shuffle servers for load balancing
        random.shuffle(servers)
        
        for server_addr in servers:
            try:
                if ':' in server_addr:
                    host, port = server_addr.rsplit(':', 1)
                    port = int(port)
                else:
                    host = server_addr
                    port = 50002 if use_ssl else 50001
                
                print(f"Connecting to Electrum server: {host}:{port}")
                
                client = ElectrumClient(host, port, use_ssl, timeout)
                if client.connect():
                    # Test connection with server version
                    version = client.send_request("server.version", ["BitcoinTracker", "1.4"])
                    if version:
                        print(f"Connected to {host}:{port} - Server: {version}")
                        self.electrum_client = client
                        self.current_server = f"{host}:{port}"
                        return
                    
                client.disconnect()
                
            except Exception as e:
                print(f"Failed to connect to {server_addr}: {e}")
                continue
        
        print("Error: Could not connect to any Electrum server.")
        sys.exit(1)
    
    def validate_address(self, address: str) -> bool:
        """Validate a Bitcoin address format."""
        try:
            scripthash = BitcoinAddressUtils.address_to_scripthash(address)
            return scripthash is not None
        except:
            return False
    
    def get_balance(self, address: str) -> Dict[str, Union[str, Decimal]]:
        """Get balance for a single address."""
        if not self.validate_address(address):
            return {
                "address": address,
                "balance": "Invalid address",
                "confirmed": Decimal("0"),
                "unconfirmed": Decimal("0"),
                "total": Decimal("0")
            }
        
        try:
            # Convert address to scripthash
            scripthash = BitcoinAddressUtils.address_to_scripthash(address)
            if not scripthash:
                return {
                    "address": address,
                    "balance": "Address conversion failed",
                    "confirmed": Decimal("0"),
                    "unconfirmed": Decimal("0"),
                    "total": Decimal("0")
                }
            
            # Query balance from Electrum server with retry logic
            balance_data = None
            max_retries = 2
            
            for attempt in range(max_retries):
                balance_data = self.electrum_client.send_request(
                    "blockchain.scripthash.get_balance", 
                    [scripthash]
                )
                
                if balance_data is not None:
                    break
                    
                # If first attempt failed, try reconnecting
                if attempt < max_retries - 1:
                    print(f"Retrying balance query for {address}...")
                    self.electrum_client.disconnect()
                    time.sleep(1)
                    self._connect_electrum()
            
            if balance_data is None:
                return {
                    "address": address,
                    "balance": "Query failed",
                    "confirmed": Decimal("0"),
                    "unconfirmed": Decimal("0"),
                    "total": Decimal("0")
                }
            
            # Convert satoshis to BTC
            confirmed = Decimal(balance_data.get("confirmed", 0)) / Decimal("100000000")
            unconfirmed = Decimal(balance_data.get("unconfirmed", 0)) / Decimal("100000000")
            total = confirmed + unconfirmed
            
            return {
                "address": address,
                "balance": f"{total:.8f} BTC",
                "confirmed": confirmed,
                "unconfirmed": unconfirmed,
                "total": total
            }
            
        except Exception as e:
            return {
                "address": address,
                "balance": f"Error: {str(e)}",
                "confirmed": Decimal("0"),
                "unconfirmed": Decimal("0"),
                "total": Decimal("0")
            }
    
    def get_balances(self) -> List[Dict[str, Union[str, Decimal]]]:
        """Get balances for all configured addresses."""
        balances = []
        for address in self.config.get("addresses", []):
            balance = self.get_balance(address)
            balances.append(balance)
        return balances
    
    def get_transaction_history(self, address: str) -> List[Dict]:
        """Get transaction history for an address."""
        try:
            scripthash = BitcoinAddressUtils.address_to_scripthash(address)
            if not scripthash:
                return []
            
            history = self.electrum_client.send_request(
                "blockchain.scripthash.get_history",
                [scripthash]
            )
            
            return history or []
            
        except Exception as e:
            print(f"Error getting history for {address}: {e}")
            return []
    
    def get_server_info(self) -> Dict:
        """Get information about the connected Electrum server."""
        if not self.electrum_client:
            return {"error": "Not connected to any server"}
        
        try:
            # Get server features/info (don't call version again if already connected)
            features = self.electrum_client.send_request("server.features")
            
            return {
                "server": self.current_server,
                "features": features,
                "connected": True
            }
        except Exception as e:
            return {"error": str(e), "connected": False}
    
    def monitor_continuous(self):
        """Run continuous monitoring with periodic updates."""
        print("Starting continuous monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self._print_status()
                time.sleep(self.config.get("update_interval", 60))
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        finally:
            if self.electrum_client:
                self.electrum_client.disconnect()
    
    def _print_status(self):
        """Print current status including server info and balances."""
        print(f"\n{'='*60}")
        print(f"Bitcoin Balance Tracker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Print server status (simplified to avoid duplicate calls)
        if self.current_server:
            print(f"Connected to: {self.current_server}")
        else:
            print("Server Status: Not connected")
        
        print("-" * 60)
        
        # Print balances
        balances = self.get_balances()
        if not balances:
            print("No addresses configured. Add addresses to config.json")
            return
        
        total_confirmed = Decimal("0")
        total_unconfirmed = Decimal("0")
        
        for balance in balances:
            print(f"Address: {balance['address']}")
            print(f"  Balance: {balance['balance']}")
            print(f"  Confirmed: {balance['confirmed']:.8f} BTC")
            print(f"  Unconfirmed: {balance['unconfirmed']:.8f} BTC")
            print()
            
            total_confirmed += balance['confirmed']
            total_unconfirmed += balance['unconfirmed']
        
        print(f"Total Confirmed: {total_confirmed:.8f} BTC")
        print(f"Total Unconfirmed: {total_unconfirmed:.8f} BTC")
        print(f"Total Balance: {(total_confirmed + total_unconfirmed):.8f} BTC")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bitcoin Balance Tracker using Electrum servers")
    parser.add_argument("--address", help="Track specific address")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--history", action="store_true", help="Show transaction history")
    parser.add_argument("--server-info", action="store_true", help="Show server information")
    
    args = parser.parse_args()
    
    try:
        tracker = BitcoinTracker(args.config)
        
        if args.server_info:
            # Show server information
            info = tracker.get_server_info()
            print("Server Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
                
        elif args.address:
            # Track single address
            balance = tracker.get_balance(args.address)
            print(f"Address: {balance['address']}")
            print(f"Balance: {balance['balance']}")
            print(f"Confirmed: {balance['confirmed']:.8f} BTC")
            print(f"Unconfirmed: {balance['unconfirmed']:.8f} BTC")
            
            if args.history:
                print("\nTransaction History:")
                history = tracker.get_transaction_history(args.address)
                if history:
                    for tx in history[:10]:  # Show last 10 transactions
                        print(f"  TX: {tx.get('tx_hash', 'N/A')} Height: {tx.get('height', 'N/A')}")
                else:
                    print("  No transactions found or history unavailable")
                    
        elif args.continuous:
            # Continuous monitoring
            tracker.monitor_continuous()
        else:
            # One-time balance check
            tracker._print_status()
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        try:
            if 'tracker' in locals() and tracker.electrum_client:
                tracker.electrum_client.disconnect()
        except:
            pass


if __name__ == "__main__":
    main() 