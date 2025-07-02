#!/usr/bin/env python3
"""
Simple test script for the Bitcoin Balance Tracker API
"""

import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8000/v1"
API_KEY = "your-secure-api-key-change-this-in-production"

# Test addresses
TEST_ADDRESSES = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Genesis block address
    "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",   # P2SH example
    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"  # Bech32 example
]


def make_request(method, endpoint, data=None):
    """Make an API request"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE}{endpoint}"
    
    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    return response


def test_health_check():
    """Test health check endpoint (no auth required)"""
    print("🔍 Testing health check...")
    response = requests.get("http://localhost:8000/health")
    
    if response.status_code == 200:
        print("✅ Health check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(response.text)
    print()


def test_api_status():
    """Test API status endpoint"""
    print("🔍 Testing API status...")
    response = make_request("GET", "/status")
    
    if response.status_code == 200:
        print("✅ API status check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ API status check failed: {response.status_code}")
        print(response.text)
    print()


def test_single_address_balance():
    """Test single address balance"""
    print("🔍 Testing single address balance...")
    address = TEST_ADDRESSES[0]
    response = make_request("GET", f"/bitcoin/balance/{address}")
    
    if response.status_code == 200:
        print(f"✅ Balance check passed for {address}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Balance check failed: {response.status_code}")
        print(response.text)
    print()


def test_multiple_addresses_balance():
    """Test multiple addresses balance"""
    print("🔍 Testing multiple addresses balance...")
    data = {"addresses": TEST_ADDRESSES[:2]}
    response = make_request("POST", "/bitcoin/balances", data)
    
    if response.status_code == 200:
        print("✅ Multiple balance check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Multiple balance check failed: {response.status_code}")
        print(response.text)
    print()


def test_address_validation():
    """Test address validation"""
    print("🔍 Testing address validation...")
    data = {"address": TEST_ADDRESSES[0]}
    response = make_request("POST", "/bitcoin/validate", data)
    
    if response.status_code == 200:
        print("✅ Address validation passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Address validation failed: {response.status_code}")
        print(response.text)
    print()


def test_server_info():
    """Test server info"""
    print("🔍 Testing server info...")
    response = make_request("GET", "/bitcoin/server-info")
    
    if response.status_code == 200:
        print("✅ Server info check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Server info check failed: {response.status_code}")
        print(response.text)
    print()


def test_unauthorized_request():
    """Test unauthorized request"""
    print("🔍 Testing unauthorized request...")
    headers = {"Content-Type": "application/json"}  # No API key
    
    response = requests.get(f"{API_BASE}/bitcoin/balance/{TEST_ADDRESSES[0]}", headers=headers)
    
    if response.status_code == 401:
        print("✅ Unauthorized request properly rejected")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Unauthorized request test failed: {response.status_code}")
        print(response.text)
    print()


def main():
    """Run all tests"""
    print("🚀 Bitcoin Balance Tracker API Test Suite\n")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test API endpoints
    test_api_status()
    test_single_address_balance()
    test_multiple_addresses_balance()
    test_address_validation()
    test_server_info()
    
    # Test security
    test_unauthorized_request()
    
    print("🏁 Test suite completed!")
    print("\nTo start the API server:")
    print("python api/main.py")
    print("\nTo view interactive docs:")
    print("http://localhost:8000/v1/docs")


if __name__ == "__main__":
    main() 