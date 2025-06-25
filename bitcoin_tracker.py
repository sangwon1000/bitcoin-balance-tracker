#!/usr/bin/env python3
"""
Bitcoin Balance Tracker

A Python application that tracks Bitcoin wallet balances using a local Bitcoin Core pruned node.
"""

import json
import argparse
import time
import sys
from decimal import Decimal
from typing import Dict, List, Optional, Union
from datetime import datetime

try:
    from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
except ImportError:
    print("Error: python-bitcoinrpc not installed. Run: pip install python-bitcoinrpc")
    sys.exit(1)


class BitcoinTracker:
    """Bitcoin balance tracker using Bitcoin Core RPC."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the tracker with configuration."""
        self.config = self._load_config(config_path)
        self.rpc_connection = None
        self._connect_rpc()
    
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
    
    def _connect_rpc(self):
        """Establish RPC connection to Bitcoin Core."""
        try:
            rpc_url = f"http://{self.config['rpc_user']}:{self.config['rpc_password']}@{self.config['rpc_host']}:{self.config['rpc_port']}"
            self.rpc_connection = AuthServiceProxy(rpc_url)
            # Test connection
            self.rpc_connection.getblockchaininfo()
        except JSONRPCException as e:
            print(f"RPC Error: {e}")
            print("Please check your Bitcoin Core configuration and ensure it's running.")
            sys.exit(1)
        except Exception as e:
            print(f"Connection Error: {e}")
            print("Please check your RPC credentials and Bitcoin Core status.")
            sys.exit(1)
    
    def validate_address(self, address: str) -> bool:
        """Validate a Bitcoin address."""
        try:
            result = self.rpc_connection.validateaddress(address)
            return result["isvalid"]
        except JSONRPCException:
            return False
    
    def get_balance(self, address: str) -> Dict[str, Union[str, Decimal]]:
        """Get balance for a single address including unconfirmed transactions."""
        if not self.validate_address(address):
            return {
                "address": address,
                "balance": "Invalid address",
                "confirmed": Decimal("0"),
                "unconfirmed": Decimal("0"),
                "total": Decimal("0"),
                "utxo_count": 0
            }
        
        try:
            # Import address to track it
            self.rpc_connection.importaddress(address, "", False)
            
            # Get confirmed balance from UTXOs
            utxos = self.rpc_connection.listunspent(0, 9999999, [address])
            confirmed_balance = sum(Decimal(str(utxo["amount"])) for utxo in utxos)
            
            # Get unconfirmed transactions from mempool
            unconfirmed_balance = Decimal("0")
            try:
                mempool = self.rpc_connection.getrawmempool(True)
                for txid, tx_info in mempool.items():
                    try:
                        tx = self.rpc_connection.getrawtransaction(txid, True)
                        for vout in tx["vout"]:
                            if "addresses" in vout["scriptPubKey"] and address in vout["scriptPubKey"]["addresses"]:
                                unconfirmed_balance += Decimal(str(vout["value"]))
                    except JSONRPCException:
                        continue
            except JSONRPCException:
                # Mempool might not be available in some configurations
                pass
            
            total_balance = confirmed_balance + unconfirmed_balance
            
            return {
                "address": address,
                "balance": f"{total_balance:.8f} BTC",
                "confirmed": confirmed_balance,
                "unconfirmed": unconfirmed_balance,
                "total": total_balance,
                "utxo_count": len(utxos)
            }
            
        except JSONRPCException as e:
            return {
                "address": address,
                "balance": f"Error: {str(e)}",
                "confirmed": Decimal("0"),
                "unconfirmed": Decimal("0"),
                "total": Decimal("0"),
                "utxo_count": 0
            }
    
    def get_balances(self) -> List[Dict[str, Union[str, Decimal]]]:
        """Get balances for all configured addresses."""
        balances = []
        for address in self.config.get("addresses", []):
            balance = self.get_balance(address)
            balances.append(balance)
        return balances
    
    def get_sync_status(self) -> Dict:
        """Get Bitcoin Core sync status."""
        try:
            info = self.rpc_connection.getblockchaininfo()
            return {
                "blocks": info.get("blocks", 0),
                "headers": info.get("headers", 0),
                "verification_progress": info.get("verificationprogress", 0),
                "pruned": info.get("pruned", False),
                "pruneheight": info.get("pruneheight", 0),
                "synced": info.get("blocks", 0) >= info.get("headers", 0)
            }
        except JSONRPCException as e:
            return {"error": str(e)}
    
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
    
    def _print_status(self):
        """Print current status including sync info and balances."""
        print(f"\n{'='*60}")
        print(f"Bitcoin Balance Tracker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Print sync status
        sync_status = self.get_sync_status()
        if "error" in sync_status:
            print(f"Sync Status: Error - {sync_status['error']}")
        else:
            progress = sync_status["verification_progress"] * 100
            print(f"Sync Status: {sync_status['blocks']}/{sync_status['headers']} blocks ({progress:.1f}%)")
            if sync_status["pruned"]:
                print(f"Pruned Node: Yes (prune height: {sync_status['pruneheight']})")
            else:
                print("Pruned Node: No")
        
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
            print(f"  UTXOs: {balance['utxo_count']}")
            print()
            
            total_confirmed += balance['confirmed']
            total_unconfirmed += balance['unconfirmed']
        
        print(f"Total Confirmed: {total_confirmed:.8f} BTC")
        print(f"Total Unconfirmed: {total_unconfirmed:.8f} BTC")
        print(f"Total Balance: {(total_confirmed + total_unconfirmed):.8f} BTC")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bitcoin Balance Tracker")
    parser.add_argument("--address", help="Track specific address")
    parser.add_argument("--continuous", action="store_true", help="Run in continuous mode")
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        tracker = BitcoinTracker(args.config)
        
        if args.address:
            # Track single address
            balance = tracker.get_balance(args.address)
            print(f"Address: {balance['address']}")
            print(f"Balance: {balance['balance']}")
            print(f"Confirmed: {balance['confirmed']:.8f} BTC")
            print(f"Unconfirmed: {balance['unconfirmed']:.8f} BTC")
            print(f"UTXOs: {balance['utxo_count']}")
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


if __name__ == "__main__":
    main() 