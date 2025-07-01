#!/usr/bin/env python3
"""
Test script to verify Electrum server connection and basic functionality.
"""

import sys
import json
from bitcoin_tracker import BitcoinTracker, ElectrumClient

def test_electrum_connection():
    """Test connection to Electrum servers."""
    print("Testing Electrum server connection...")
    
    # Test servers
    test_servers = [
        ("electrum.hsmiths.com", 50002),
        ("stavver.dyshek.org", 50002),
    ]
    
    for host, port in test_servers:
        print(f"\nTesting {host}:{port}...")
        
        client = ElectrumClient(host, port, use_ssl=True, timeout=5)
        
        if client.connect():
            print(f"✓ Connected successfully!")
            
            # Test server version
            version = client.send_request("server.version", ["TestClient", "1.4"])
            if version:
                print(f"✓ Server version: {version}")
            else:
                print("✗ Failed to get server version")
            
            # Test server features
            features = client.send_request("server.features")
            if features:
                print(f"✓ Server features available")
                if 'server_version' in features:
                    print(f"  Server version: {features['server_version']}")
                if 'protocol_max' in features:
                    print(f"  Protocol version: {features['protocol_max']}")
            else:
                print("✗ Failed to get server features")
                
            client.disconnect()
            print(f"✓ Disconnected from {host}")
            return True
        else:
            print(f"✗ Failed to connect to {host}:{port}")
    
    return False

def test_address_conversion():
    """Test Bitcoin address to scripthash conversion."""
    from bitcoin_tracker import BitcoinAddressUtils
    
    print("\n" + "="*50)
    print("Testing address to scripthash conversion...")
    
    # Test addresses
    test_addresses = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block coinbase (P2PKH)
        "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",   # P2SH address
        # Note: bech32 conversion is simplified in our implementation
    ]
    
    for address in test_addresses:
        print(f"\nTesting address: {address}")
        try:
            scripthash = BitcoinAddressUtils.address_to_scripthash(address)
            if scripthash:
                print(f"✓ Scripthash: {scripthash}")
            else:
                print("✗ Failed to convert address")
        except Exception as e:
            print(f"✗ Error: {e}")

def test_balance_query():
    """Test balance querying with known addresses."""
    print("\n" + "="*50)
    print("Testing balance queries...")
    
    # Test with a known address (Genesis block coinbase)
    test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    
    try:
        # Create a simple config for testing
        test_config = {
            "electrum_servers": [
                "electrum.hsmiths.com:50002",
                "stavver.dyshek.org:50002"
            ],
            "use_ssl": True,
            "timeout": 10,
            "addresses": [test_address]
        }
        
        # Save temporary config
        with open("test_config.json", "w") as f:
            json.dump(test_config, f, indent=2)
        
        print(f"Testing balance query for: {test_address}")
        
        tracker = BitcoinTracker("test_config.json")
        balance = tracker.get_balance(test_address)
        
        print(f"Result: {balance}")
        
        if "Error" not in balance["balance"]:
            print("✓ Balance query successful!")
        else:
            print("✗ Balance query failed")
        
        # Clean up
        tracker.electrum_client.disconnect()
        
        # Remove test config
        import os
        os.remove("test_config.json")
        
    except Exception as e:
        print(f"✗ Error during balance query: {e}")

def main():
    """Run all tests."""
    print("Bitcoin Balance Tracker - Electrum Connection Test")
    print("=" * 60)
    
    try:
        # Test 1: Basic connection
        if not test_electrum_connection():
            print("\n✗ All Electrum server connections failed!")
            print("This might be due to network issues or server unavailability.")
            sys.exit(1)
        
        # Test 2: Address conversion
        test_address_conversion()
        
        # Test 3: Balance query
        test_balance_query()
        
        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("\nYour system is ready to use the Bitcoin Balance Tracker with Electrum servers.")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 