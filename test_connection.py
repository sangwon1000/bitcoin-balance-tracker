#!/usr/bin/env python3
"""
Test script to verify Bitcoin Core connection and configuration.
Run this after setting up Bitcoin Core to ensure everything is working.
"""

import json
import sys

try:
    from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
except ImportError:
    print("Error: python-bitcoinrpc not installed. Run: pip install python-bitcoinrpc")
    sys.exit(1)


def test_connection():
    """Test Bitcoin Core RPC connection."""
    print("Bitcoin Core Connection Test")
    print("=" * 40)
    
    # Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please copy config.example.json to config.json and update it.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json: {e}")
        return False
    
    # Test RPC connection
    try:
        rpc_url = f"http://{config['rpc_user']}:{config['rpc_password']}@{config['rpc_host']}:{config['rpc_port']}"
        rpc = AuthServiceProxy(rpc_url)
        
        print("✓ RPC connection established")
        
        # Get blockchain info
        info = rpc.getblockchaininfo()
        print(f"✓ Bitcoin Core version: {info.get('version', 'Unknown')}")
        print(f"✓ Blocks: {info.get('blocks', 0)}")
        print(f"✓ Headers: {info.get('headers', 0)}")
        print(f"✓ Pruned: {info.get('pruned', False)}")
        
        if info.get('pruned'):
            print(f"✓ Prune height: {info.get('pruneheight', 0)}")
        
        # Check sync status
        progress = info.get('verificationprogress', 0) * 100
        print(f"✓ Sync progress: {progress:.1f}%")
        
        if info.get('blocks', 0) >= info.get('headers', 0):
            print("✓ Node is fully synced")
        else:
            print("⚠ Node is still syncing")
        
        # Test address validation
        test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        result = rpc.validateaddress(test_address)
        if result["isvalid"]:
            print("✓ Address validation working")
        else:
            print("⚠ Address validation failed")
        
        print("\n✓ All tests passed! Your Bitcoin Core setup is working correctly.")
        return True
        
    except JSONRPCException as e:
        print(f"✗ RPC Error: {e}")
        print("Please check your Bitcoin Core configuration and ensure it's running.")
        return False
    except Exception as e:
        print(f"✗ Connection Error: {e}")
        print("Please check your RPC credentials and Bitcoin Core status.")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 