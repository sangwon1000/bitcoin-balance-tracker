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
import threading
import concurrent.futures

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


class ElectrumServerDiscovery:
    """Automated Electrum server discovery and health monitoring."""
    
    # Known good seed servers for initial discovery
    SEED_SERVERS = [
        "electrum.hsmiths.com:50002",
        "fortress.qtornado.com:443", 
        "electrum.blockstream.info:50002",
        "electrum.acinq.co:50002",
        "bitcoin.electrum.blockstream.info:50002",
        "kris.at:50002",
        "ecdsa.net:50002",
        "mempool.space:50002",
    ]
    
    def __init__(self, use_ssl: bool = True, timeout: int = 10, max_servers: int = 20):
        """Initialize server discovery."""
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.max_servers = max_servers
        self.discovered_servers = {}  # {host:port -> {health_score, last_tested, features}}
        self.lock = threading.Lock()
        
    def discover_servers(self, seed_servers: List[str] = None) -> List[str]:
        """Discover Electrum servers using peer discovery protocol."""
        if seed_servers is None:
            seed_servers = self.SEED_SERVERS.copy()
        
        print("🔍 Discovering Electrum servers...")
        discovered = set()
        
        # Test seed servers and get their peer lists
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_server = {
                executor.submit(self._discover_from_server, server): server 
                for server in seed_servers
            }
            
            for future in concurrent.futures.as_completed(future_to_server):
                server = future_to_server[future]
                try:
                    peers = future.result()
                    if peers:
                        discovered.update(peers)
                        print(f"✅ {server}: Found {len(peers)} peers")
                    else:
                        print(f"❌ {server}: No peers found")
                except Exception as e:
                    print(f"❌ {server}: Discovery failed - {e}")
        
        # Health check discovered servers
        healthy_servers = self._health_check_servers(list(discovered))
        
        # Sort by health score
        sorted_servers = sorted(
            healthy_servers,
            key=lambda x: self.discovered_servers.get(x, {}).get('health_score', 0),
            reverse=True
        )
        
        result = sorted_servers[:self.max_servers]
        print(f"🎯 Found {len(result)} healthy Electrum servers")
        return result
    
    def _discover_from_server(self, server_addr: str) -> List[str]:
        """Discover peer servers from a single server."""
        try:
            if ':' in server_addr:
                host, port = server_addr.rsplit(':', 1)
                port = int(port)
            else:
                host = server_addr
                port = 50002 if self.use_ssl else 50001
            
            # Connect and get peer list
            client = ElectrumClient(host, port, self.use_ssl, self.timeout)
            if not client.connect():
                return []
            
            # Request peer list
            peers = client.send_request("server.peers.subscribe")
            client.disconnect()
            
            if not peers:
                return []
            
            # Parse peer list
            discovered = []
            for peer_info in peers:
                if len(peer_info) >= 3:
                    peer_host = peer_info[1]  # hostname
                    features = peer_info[2] if len(peer_info) > 2 else []
                    
                    # Extract SSL and TCP ports from features array
                    ssl_port = None
                    tcp_port = None
                    
                    if isinstance(features, list):
                        for feature in features:
                            if isinstance(feature, str):
                                if feature.startswith('s'):
                                    ssl_port = feature[1:]  # Remove 's' prefix
                                elif feature.startswith('t'):
                                    tcp_port = feature[1:]  # Remove 't' prefix
                    
                    # Prefer SSL port
                    if self.use_ssl and ssl_port:
                        discovered.append(f"{peer_host}:{ssl_port}")
                    elif tcp_port:
                        discovered.append(f"{peer_host}:{tcp_port}")
                    elif ssl_port:  # Fallback to SSL even if not preferred
                        discovered.append(f"{peer_host}:{ssl_port}")
            
            return discovered
            
        except Exception:
            return []
    
    def _health_check_servers(self, servers: List[str]) -> List[str]:
        """Health check multiple servers in parallel."""
        healthy = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_server = {
                executor.submit(self._health_check_single, server): server 
                for server in servers
            }
            
            for future in concurrent.futures.as_completed(future_to_server):
                server = future_to_server[future]
                try:
                    is_healthy = future.result()
                    if is_healthy:
                        healthy.append(server)
                except Exception:
                    pass  # Already handled in _health_check_single
        
        return healthy
    
    def _health_check_single(self, server_addr: str) -> bool:
        """Health check a single server."""
        try:
            if ':' in server_addr:
                host, port = server_addr.rsplit(':', 1)
                port = int(port)
            else:
                host = server_addr
                port = 50002 if self.use_ssl else 50001
            
            start_time = time.time()
            
            # Quick connection test
            client = ElectrumClient(host, port, self.use_ssl, self.timeout)
            if not client.connect():
                return False
            
            # Test basic functionality
            version = client.send_request("server.version", ["HealthCheck", "1.4"])
            features = client.send_request("server.features")
            
            latency = time.time() - start_time
            client.disconnect()
            
            if version and features:
                # Calculate health score (lower latency = higher score)
                health_score = max(0, 100 - (latency * 10))
                
                with self.lock:
                    self.discovered_servers[server_addr] = {
                        'health_score': health_score,
                        'latency': latency,
                        'last_tested': time.time(),
                        'features': features,
                        'version': version
                    }
                
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_best_servers(self, count: int = 5) -> List[str]:
        """Get the best servers by health score."""
        with self.lock:
            sorted_servers = sorted(
                self.discovered_servers.items(),
                key=lambda x: x[1].get('health_score', 0),
                reverse=True
            )
        
        return [server for server, _ in sorted_servers[:count]]
    
    def update_server_list(self, current_servers: List[str]) -> List[str]:
        """Update server list with fresh discoveries."""
        # Discover new servers
        fresh_servers = self.discover_servers(current_servers)
        
        # Combine with existing servers and remove duplicates
        combined = list(set(current_servers + fresh_servers))
        
        # Re-health check all servers
        healthy_servers = self._health_check_servers(combined)
        
        # Return best servers
        return self.get_best_servers(min(len(healthy_servers), self.max_servers))


class BitcoinAddressUtils:
    """Complete Bitcoin address decoder supporting all major address types."""
    
    # Bech32 character set
    BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    
    @staticmethod
    def bech32_polymod(values):
        """Compute bech32 polymod for checksum validation."""
        GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for value in values:
            top = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ value
            for i in range(5):
                chk ^= GEN[i] if ((top >> i) & 1) else 0
        return chk
    
    @staticmethod
    def bech32_hrp_expand(hrp):
        """Expand human readable part for bech32."""
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
    
    @staticmethod
    def bech32_verify_checksum(hrp, data, spec):
        """Verify bech32 or bech32m checksum."""
        const = 1 if spec == "bech32" else 0x2bc830a3
        return BitcoinAddressUtils.bech32_polymod(
            BitcoinAddressUtils.bech32_hrp_expand(hrp) + data
        ) == const
    
    @staticmethod
    def convertbits(data, frombits, tobits, pad=True):
        """Convert between bit groups."""
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        max_acc = (1 << (frombits + tobits - 1)) - 1
        for value in data:
            if value < 0 or (value >> frombits):
                return None
            acc = ((acc << frombits) | value) & max_acc
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad:
            if bits:
                ret.append((acc << (tobits - bits)) & maxv)
        elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
            return None
        return ret
    
    @staticmethod
    def decode_bech32(address):
        """Decode bech32 address (SegWit v0)."""
        if not address.startswith('bc1'):
            return None
            
        try:
            # Split address
            if address.rfind('1') == -1:
                return None
            hrp = address[:address.rfind('1')]
            data_part = address[address.rfind('1')+1:]
            
            # Convert to numbers
            data = []
            for char in data_part:
                if char not in BitcoinAddressUtils.BECH32_CHARSET:
                    return None
                data.append(BitcoinAddressUtils.BECH32_CHARSET.index(char))
            
            # Verify checksum
            if not BitcoinAddressUtils.bech32_verify_checksum(hrp, data, "bech32"):
                return None
            
            # Extract witness version and program
            if len(data) < 6:
                return None
            witness_version = data[0]
            program = BitcoinAddressUtils.convertbits(data[1:-6], 5, 8, False)
            
            if program is None or len(program) < 2 or len(program) > 40:
                return None
                
            if witness_version == 0:
                if len(program) == 20:  # P2WPKH
                    script = bytes([0x00, 0x14]) + bytes(program)
                    script_hash = hashlib.sha256(script).digest()
                    return script_hash[::-1].hex()
                elif len(program) == 32:  # P2WSH
                    script = bytes([0x00, 0x20]) + bytes(program)
                    script_hash = hashlib.sha256(script).digest()
                    return script_hash[::-1].hex()
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def decode_bech32m(address):
        """Decode bech32m address (Taproot)."""
        if not address.startswith('bc1p'):
            return None
            
        try:
            # Split address
            if address.rfind('1') == -1:
                return None
            hrp = address[:address.rfind('1')]
            data_part = address[address.rfind('1')+1:]
            
            # Convert to numbers
            data = []
            for char in data_part:
                if char not in BitcoinAddressUtils.BECH32_CHARSET:
                    return None
                data.append(BitcoinAddressUtils.BECH32_CHARSET.index(char))
            
            # Verify bech32m checksum
            if not BitcoinAddressUtils.bech32_verify_checksum(hrp, data, "bech32m"):
                return None
            
            # Extract witness version and program
            if len(data) < 6:
                return None
            witness_version = data[0]
            program = BitcoinAddressUtils.convertbits(data[1:-6], 5, 8, False)
            
            if program is None or witness_version != 1 or len(program) != 32:
                return None
                
            # P2TR script
            script = bytes([0x51, 0x20]) + bytes(program)  # OP_1 + 32 bytes
            script_hash = hashlib.sha256(script).digest()
            return script_hash[::-1].hex()
            
        except Exception:
            return None
    
    @staticmethod
    def decode_legacy(address):
        """Decode legacy address (P2PKH or P2SH)."""
        try:
            decoded = base58.b58decode(address)
            payload = decoded[:-4]
            version = payload[0]
            hash160 = payload[1:]
            
            if len(hash160) != 20:
                return None
                
            if version == 0x00:  # P2PKH
                script = bytes([0x76, 0xa9, 0x14]) + hash160 + bytes([0x88, 0xac])
            elif version == 0x05:  # P2SH
                script = bytes([0xa9, 0x14]) + hash160 + bytes([0x87])
            else:
                return None
                
            script_hash = hashlib.sha256(script).digest()
            return script_hash[::-1].hex()
            
        except Exception:
            return None
    
    @staticmethod
    def address_to_scripthash(address):
        """Convert any Bitcoin address to scripthash for Electrum queries."""
        # Determine address type and decode accordingly
        if address.startswith('1'):
            return BitcoinAddressUtils.decode_legacy(address)
        elif address.startswith('3'):
            return BitcoinAddressUtils.decode_legacy(address)
        elif address.startswith('bc1q'):
            return BitcoinAddressUtils.decode_bech32(address)
        elif address.startswith('bc1p'):
            return BitcoinAddressUtils.decode_bech32m(address)
        else:
            return None
    
    @staticmethod
    def get_address_type(address):
        """Get the type of Bitcoin address."""
        if address.startswith('1'):
            return "P2PKH (Legacy)"
        elif address.startswith('3'):
            return "P2SH (Script)"
        elif address.startswith('bc1q'):
            if len(address) == 42:
                return "P2WPKH (SegWit)"
            elif len(address) == 62:
                return "P2WSH (SegWit Script)"
            else:
                return "Unknown SegWit"
        elif address.startswith('bc1p'):
            return "P2TR (Taproot)"
        else:
            return "Unknown"




class BitcoinTracker:
    """Bitcoin balance tracker using public Electrum servers."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the tracker with configuration."""
        self.config = self._load_config(config_path)
        self.electrum_client = None
        self.current_server = None
        self.server_discovery = None
        
        # Initialize server discovery if enabled
        if self.config.get("enable_server_discovery", False):
            self.server_discovery = ElectrumServerDiscovery(
                use_ssl=self.config.get("use_ssl", True),
                timeout=self.config.get("timeout", 10),
                max_servers=self.config.get("max_discovered_servers", 20)
            )
        
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
        
        # Try configured servers first
        if servers:
            # Shuffle servers for load balancing
            random.shuffle(servers)
            
            for server_addr in servers:
                if self._try_connect_server(server_addr, use_ssl, timeout):
                    return
        
        # If no configured servers or all failed, try server discovery
        if self.server_discovery:
            print("📡 Configured servers failed, trying server discovery...")
            discovered_servers = self.server_discovery.discover_servers(servers if servers else None)
            
            for server_addr in discovered_servers:
                if self._try_connect_server(server_addr, use_ssl, timeout):
                    return
        
        # Final fallback to seed servers
        if not servers or not self.server_discovery:
            print("🔄 Trying fallback seed servers...")
            seed_servers = ElectrumServerDiscovery.SEED_SERVERS
            random.shuffle(seed_servers)
            
            for server_addr in seed_servers:
                if self._try_connect_server(server_addr, use_ssl, timeout):
                    return
        
        print("❌ Error: Could not connect to any Electrum server.")
        sys.exit(1)
    
    def _try_connect_server(self, server_addr: str, use_ssl: bool, timeout: int) -> bool:
        """Try to connect to a single server."""
        try:
            if ':' in server_addr:
                host, port = server_addr.rsplit(':', 1)
                port = int(port)
            else:
                host = server_addr
                port = 50002 if use_ssl else 50001
            
            print(f"🔌 Connecting to Electrum server: {host}:{port}")
            
            client = ElectrumClient(host, port, use_ssl, timeout)
            if client.connect():
                # Test connection with server version
                version = client.send_request("server.version", ["BitcoinTracker", "1.4"])
                if version:
                    print(f"✅ Connected to {host}:{port} - Server: {version}")
                    self.electrum_client = client
                    self.current_server = f"{host}:{port}"
                    return True
                
            client.disconnect()
            
        except Exception as e:
            print(f"❌ Failed to connect to {server_addr}: {e}")
        
        return False
    
    def validate_address(self, address: str) -> bool:
        """Validate a Bitcoin address format."""
        try:
            scripthash = BitcoinAddressUtils.address_to_scripthash(address)
            return scripthash is not None
        except:
            return False
    
    def get_address_type(self, address: str) -> str:
        """Get the type of Bitcoin address."""
        return BitcoinAddressUtils.get_address_type(address)
    
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
    
    def discover_servers(self) -> List[str]:
        """Manually trigger server discovery."""
        if not self.server_discovery:
            self.server_discovery = ElectrumServerDiscovery(
                use_ssl=self.config.get("use_ssl", True),
                timeout=self.config.get("timeout", 10),
                max_servers=self.config.get("max_discovered_servers", 20)
            )
        
        return self.server_discovery.discover_servers()
    
    def update_server_list(self) -> List[str]:
        """Update and refresh the server list."""
        if not self.server_discovery:
            print("❌ Server discovery not enabled in config")
            return []
        
        current_servers = self.config.get("electrum_servers", [])
        return self.server_discovery.update_server_list(current_servers)
    
    def save_discovered_servers(self, servers: List[str], config_path: str = None):
        """Save discovered servers to config file."""
        if not servers:
            print("❌ No servers to save")
            return
        
        if config_path is None:
            config_path = "config.json"
        
        # Update config
        self.config["electrum_servers"] = servers
        
        # Save to file
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"✅ Saved {len(servers)} servers to {config_path}")
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
    
    def show_discovery_status(self):
        """Show current server discovery status and health scores."""
        if not self.server_discovery:
            print("❌ Server discovery not initialized")
            return
        
        print("\n" + "="*60)
        print("🔍 SERVER DISCOVERY STATUS")
        print("="*60)
        
        with self.server_discovery.lock:
            if not self.server_discovery.discovered_servers:
                print("No servers discovered yet. Run discovery first.")
                return
            
            sorted_servers = sorted(
                self.server_discovery.discovered_servers.items(),
                key=lambda x: x[1].get('health_score', 0),
                reverse=True
            )
            
            print(f"{'Server':<35} {'Health':<8} {'Latency':<10} {'Last Tested':<15}")
            print("-" * 75)
            
            for server, data in sorted_servers:
                health = f"{data.get('health_score', 0):.1f}"
                latency = f"{data.get('latency', 0):.2f}s"
                last_tested = datetime.fromtimestamp(
                    data.get('last_tested', 0)
                ).strftime('%H:%M:%S')
                
                print(f"{server:<35} {health:<8} {latency:<10} {last_tested:<15}")
    
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
            addr_type = self.get_address_type(balance['address'])
            print(f"Address: {balance['address']}")
            print(f"  Type: {addr_type}")
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
    
    # Server discovery options
    parser.add_argument("--discover-servers", action="store_true", help="Discover and test Electrum servers")
    parser.add_argument("--update-servers", action="store_true", help="Update server list with fresh discoveries")
    parser.add_argument("--save-servers", action="store_true", help="Save discovered servers to config")
    parser.add_argument("--show-discovery", action="store_true", help="Show server discovery status and health scores")
    
    args = parser.parse_args()
    
    try:
        tracker = BitcoinTracker(args.config)
        
        # Handle server discovery commands
        if args.discover_servers:
            print("🔍 Starting server discovery...")
            servers = tracker.discover_servers()
            print(f"\n📋 Discovered {len(servers)} servers:")
            for i, server in enumerate(servers, 1):
                print(f"  {i:2d}. {server}")
            
            if args.save_servers and servers:
                tracker.save_discovered_servers(servers, args.config)
                
        elif args.update_servers:
            print("🔄 Updating server list...")
            servers = tracker.update_server_list()
            print(f"\n📋 Updated server list ({len(servers)} servers):")
            for i, server in enumerate(servers, 1):
                print(f"  {i:2d}. {server}")
            
            if args.save_servers and servers:
                tracker.save_discovered_servers(servers, args.config)
                
        elif args.show_discovery:
            tracker.show_discovery_status()
            
        elif args.server_info:
            # Show server information
            info = tracker.get_server_info()
            print("Server Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
                
        elif args.address:
            # Track single address
            balance = tracker.get_balance(args.address)
            addr_type = tracker.get_address_type(args.address)
            print(f"Address: {balance['address']}")
            print(f"Type: {addr_type}")
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