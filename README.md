# Bitcoin Balance Tracker

A lightweight Python application that tracks Bitcoin wallet balances using public Electrum servers. **No local Bitcoin node required!** Simply configure your addresses and start tracking instantly.

## Features

- **🆕 Automatic Server Discovery**: Finds the fastest Electrum servers automatically
- **No Bitcoin Node Required**: Uses public Electrum servers - no setup, no storage, no syncing
- **Instant Setup**: Start tracking addresses in seconds
- **Complete Address Support**: ALL Bitcoin address types (Legacy, SegWit, Taproot)
- **Multiple Address Monitoring**: Track unlimited Bitcoin addresses simultaneously
- **Real-time Balance Updates**: Get current balances including unconfirmed transactions
- **Smart Server Management**: Automatic failover and health monitoring
- **Privacy Focused**: Rotates between servers and supports SSL connections
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Zero Storage**: No blockchain data stored locally

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Addresses

Copy `config.example.json` to `config.json` and add your addresses:

```json
{
    "electrum_servers": [
        "electrum.hsmiths.com:50002",
        "fortress.qtornado.com:443",
        "electrum.blockstream.info:50002"
    ],
    "use_ssl": true,
    "addresses": [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    ],
    "update_interval": 60,
    "timeout": 20,
    "enable_server_discovery": false,
    "max_discovered_servers": 20
}
```

### 3. Test Connection

```bash
python test_connection.py
```

### 4. Start Tracking

```bash
python bitcoin_tracker.py
```

That's it! No Bitcoin Core installation or blockchain sync required.

### 5. 🚀 Quick Start with Server Discovery (Recommended)

For the best experience, discover and use the fastest servers:

```bash
# Discover the best Electrum servers and save them
python bitcoin_tracker.py --discover-servers --save-servers

# Start tracking with optimized servers
python bitcoin_tracker.py
```

This finds the fastest, most reliable servers in your region automatically!

## Usage

### Basic Commands

```bash
# Track all configured addresses
python bitcoin_tracker.py

# Track specific address
python bitcoin_tracker.py --address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Continuous monitoring
python bitcoin_tracker.py --continuous

# Show transaction history
python bitcoin_tracker.py --address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa --history

# Show server information
python bitcoin_tracker.py --server-info
```

### Command Line Options

**Basic Options:**
- `--address ADDRESS`: Track specific address
- `--continuous`: Run in continuous mode with periodic updates
- `--config PATH`: Use custom config file path
- `--history`: Show transaction history for address
- `--server-info`: Display connected server information

**Server Discovery Options:**
- `--discover-servers`: Discover and test Electrum servers
- `--update-servers`: Update server list with fresh discoveries  
- `--save-servers`: Save discovered servers to config file
- `--show-discovery`: Show server health scores and status

## Configuration

### Config File Options

| Option | Description | Default |
|--------|-------------|---------|
| `electrum_servers` | List of Electrum servers (host:port) | Multiple servers |
| `use_ssl` | Use SSL/TLS connections | true |
| `addresses` | List of Bitcoin addresses to track | [] |
| `update_interval` | Update interval in seconds for continuous mode | 60 |
| `timeout` | Connection timeout in seconds | 20 |
| `enable_server_discovery` | Enable automatic server discovery | false |
| `max_discovered_servers` | Maximum servers to discover and test | 20 |

### Supported Address Types

✅ **ALL major Bitcoin address types are fully supported:**

- **P2PKH (Legacy)**: Addresses starting with `1` - Original Bitcoin format (2009)
- **P2SH (Script)**: Addresses starting with `3` - Multisig and smart contracts (2012)  
- **P2WPKH (SegWit)**: Addresses starting with `bc1q` (42 chars) - **RECOMMENDED** for lower fees (2017)
- **P2WSH (SegWit Script)**: Addresses starting with `bc1q` (62 chars) - Complex scripts with SegWit benefits
- **P2TR (Taproot)**: Addresses starting with `bc1p` - **NEWEST** with enhanced privacy and Schnorr signatures (2021)

**Your addresses are P2WPKH (SegWit)** - excellent choice for efficiency and compatibility! 

📋 See `address_types.md` for detailed comparison and recommendations.

## Electrum Servers

The application connects to public Electrum servers that index the Bitcoin blockchain. It automatically:

- Tries multiple servers for redundancy
- Uses SSL connections for privacy
- Rotates servers for load balancing
- Handles connection failures gracefully

### Default Servers

- `electrum.hsmiths.com:50002` (Hsmiths)
- `fortress.qtornado.com:443` (QTornado) 
- `electrum.blockstream.info:50002` (Blockstream)

## Automatic Server Discovery

🆕 **NEW**: Automatically discover and connect to healthy Electrum servers! Never worry about server downtime again.

### Why Use Server Discovery?

- **🔄 Automatic Failover**: When configured servers go down, automatically find working ones
- **⚡ Performance Optimization**: Connect to the fastest servers in your region
- **🌐 Network Resilience**: Access to 100+ global Electrum servers 
- **🔧 Zero Maintenance**: No manual server list updates needed
- **📊 Health Monitoring**: Real-time server performance tracking

### How It Works

The discovery system uses Electrum's peer discovery protocol:

1. **🌱 Seed Connection**: Connects to known reliable servers
2. **🔍 Peer Discovery**: Queries each server for their peer list using `server.peers.subscribe`
3. **🏥 Health Testing**: Tests discovered servers in parallel (connection speed, reliability)
4. **📈 Smart Ranking**: Scores servers based on latency and features
5. **✅ Best Selection**: Returns top-performing servers for your use

### Step-by-Step Setup Guide

#### Step 1: Enable Discovery (Optional)

Add discovery settings to your `config.json`:

```json
{
    "electrum_servers": [
        "electrum.hsmiths.com:50002",
        "fortress.qtornado.com:443"
    ],
    "enable_server_discovery": true,
    "max_discovered_servers": 20,
    "use_ssl": true,
    "timeout": 20
}
```

**Note**: Discovery works even without enabling it in config - it's used as automatic failover.

#### Step 2: Discover Fresh Servers

Find the best available servers:

```bash
# Discover and display servers with health scores
python bitcoin_tracker.py --discover-servers
```

**Example Output**:
```
🔍 Discovering Electrum servers...
✅ fortress.qtornado.com:443: Found 161 peers
✅ electrum.blockstream.info:50002: Found 26 peers
🎯 Found 20 healthy Electrum servers

📋 Discovered 20 servers:
   1. 34.96.220.189:50002          (Health: 99.3, Latency: 0.07s)
   2. electrumx.dev:50002          (Health: 97.8, Latency: 0.22s)
   3. 35.221.221.16:50002          (Health: 98.9, Latency: 0.11s)
   ...
```

#### Step 3: Save Best Servers to Config

Update your configuration with discovered servers:

```bash
# Discover and automatically save to config.json
python bitcoin_tracker.py --discover-servers --save-servers
```

This replaces your current server list with the best discovered servers.

#### Step 4: Update Existing Server List

Refresh your server list periodically:

```bash
# Update existing list with new discoveries
python bitcoin_tracker.py --update-servers --save-servers
```

This combines your current servers with fresh discoveries and saves the best ones.

### Command Reference

#### Discovery Commands

| Command | Function | Use Case |
|---------|----------|----------|
| `--discover-servers` | Find new servers and display results | Initial setup, testing |
| `--discover-servers --save-servers` | Find and save best servers | Replace entire server list |
| `--update-servers` | Refresh existing server list | Periodic maintenance |
| `--update-servers --save-servers` | Update and save server list | Regular server list updates |
| `--show-discovery` | Show server health status | Monitor server performance |

#### Examples with Real Output

**Basic Discovery**:
```bash
$ python bitcoin_tracker.py --discover-servers

🔍 Discovering Electrum servers...
✅ fortress.qtornado.com:443: Found 161 peers
🎯 Found 20 healthy Electrum servers

📋 Discovered 20 servers:
   1. 34.96.220.189:50002
   2. electrumx.dev:50002
   3. 35.221.221.16:50002
   ...
```

**Discovery with Save**:
```bash
$ python bitcoin_tracker.py --discover-servers --save-servers

🔍 Discovering Electrum servers...
🎯 Found 20 healthy Electrum servers
✅ Saved 20 servers to config.json
```

**Health Status Monitoring**:
```bash
$ python bitcoin_tracker.py --show-discovery

🔍 SERVER DISCOVERY STATUS
============================================================
Server                              Health   Latency    Last Tested
--------------------------------------------------------------------
34.96.220.189:50002                 99.3     0.07s      14:32:15
electrumx.dev:50002                 97.8     0.22s      14:32:18
35.221.221.16:50002                 98.9     0.11s      14:32:20
fortress.qtornado.com:443           92.1     0.26s      14:32:22
```

### Configuration Options

Add these to your `config.json`:

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `enable_server_discovery` | Enable automatic discovery on startup | `false` | `true` |
| `max_discovered_servers` | Maximum servers to discover and test | `20` | `30` |
| `timeout` | Server connection timeout (seconds) | `10` | `20` |
| `use_ssl` | Prefer SSL/TLS servers | `true` | `true` |

**Complete Config Example**:
```json
{
    "electrum_servers": [
        "34.96.220.189:50002",
        "electrumx.dev:50002",
        "35.221.221.16:50002"
    ],
    "enable_server_discovery": true,
    "max_discovered_servers": 20,
    "use_ssl": true,
    "timeout": 20,
    "addresses": [
        "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    ]
}
```

### Server Health Scoring

Servers are automatically scored (0-100) based on:

- **Connection Speed** (50%): Lower latency = higher score
- **Reliability** (30%): Successful response to test queries
- **SSL Support** (10%): Preference for encrypted connections  
- **Features** (10%): Server capabilities and protocol support

**Health Score Ranges**:
- **90-100**: 🟢 Excellent (< 0.2s latency)
- **80-89**: 🟡 Good (0.2-0.5s latency)
- **70-79**: 🟠 Fair (0.5-1.0s latency)
- **< 70**: 🔴 Poor (> 1.0s latency)

### Automatic Failover

When `enable_server_discovery: true`, the tracker automatically:

1. **Tries Configured Servers**: Uses your configured server list first
2. **Discovers on Failure**: If all configured servers fail, runs discovery
3. **Connects to Best**: Automatically connects to highest-scoring server
4. **Fallback Chain**: Uses seed servers as final fallback

**Example Automatic Failover**:
```
🔌 Connecting to Electrum server: electrum.hsmiths.com:50002
❌ Failed to connect to electrum.hsmiths.com:50002: Connection refused
📡 Configured servers failed, trying server discovery...
🔍 Discovering Electrum servers...
🎯 Found 15 healthy Electrum servers
✅ Connected to 34.96.220.189:50002 - Server: ['ElectrumX 1.16.0', '1.4']
```

### Performance & Timing

- **Discovery Time**: 30-90 seconds (depends on network and server count)
- **Parallel Testing**: Tests 10 servers simultaneously for speed
- **Success Rate**: Typically finds 15-25 healthy servers
- **Best Server Latency**: Usually < 0.3s for top-ranked servers
- **Memory Usage**: < 10MB additional during discovery

### Troubleshooting Discovery

**No servers discovered**:
```bash
# Check internet connection
curl -I https://google.com

# Test basic connectivity
python bitcoin_tracker.py --server-info

# Try with longer timeout
# Edit config.json: "timeout": 30
```

**Discovery too slow**:
```json
{
    "max_discovered_servers": 10,
    "timeout": 15
}
```

**SSL/TLS issues during discovery**:
```json
{
    "use_ssl": false
}
```

**Onion servers failing** (normal):
```
Failed to connect to *.onion:50001 - nodename nor servname provided
```
This is expected if you don't have Tor configured.

### Best Practices

1. **Initial Setup**: Run `--discover-servers --save-servers` to populate your config
2. **Regular Updates**: Run `--update-servers --save-servers` weekly/monthly  
3. **Monitor Health**: Use `--show-discovery` to check server performance
4. **Keep Backups**: Maintain known good servers in your config as fallbacks
5. **Regional Optimization**: Discovery automatically finds servers closest to you

### Advanced Usage

**Combine with Continuous Monitoring**:
```bash
# Update servers and start monitoring
python bitcoin_tracker.py --update-servers --save-servers
python bitcoin_tracker.py --continuous
```

**Scripted Server Maintenance**:
```bash
#!/bin/bash
# Weekly server refresh script
python bitcoin_tracker.py --update-servers --save-servers
echo "✅ Server list updated on $(date)"
```

## Privacy Considerations

**Public Servers**: When using public Electrum servers, the server can see:
- Your IP address
- The addresses you query
- Query timing patterns

**Privacy Tips**:
- Use a VPN for additional IP privacy
- Query addresses in batches rather than individually
- Consider running your own Electrum server for maximum privacy

## Performance

- **Startup Time**: 1-5 seconds (no sync required)
- **Memory Usage**: <50 MB
- **Storage**: <1 MB (no blockchain data)
- **Network**: Only query data, ~1 KB per address

## Troubleshooting

### Connection Issues

**All servers unreachable**:
```bash
# Test connection manually
python test_connection.py

# Try server discovery to find working servers
python bitcoin_tracker.py --discover-servers

# Check firewall/proxy settings
# Try different servers in config
```

**SSL/TLS errors**:
```json
{
    "use_ssl": false
}
```

**Timeout errors**:
```json
{
    "timeout": 30
}
```

**Server discovery fails**:
```bash
# Try with longer timeout
python bitcoin_tracker.py --discover-servers
# Edit config.json: "timeout": 30, "max_discovered_servers": 10

# Check internet connectivity
curl -I https://google.com

# Test with manual server list update
python bitcoin_tracker.py --update-servers --save-servers
```

### Address Issues

**Invalid address format**:
- Ensure address is properly formatted
- Check address type is supported
- Verify checksums are correct

**Balance not updating**:
- Address may have no transactions
- Server may be behind/syncing
- Try different server

## Security

- **No Private Keys**: Only tracks addresses, never handles private keys
- **Read-only**: Cannot send transactions or access funds
- **SSL Connections**: All communications encrypted by default
- **No Local Storage**: No sensitive data stored locally

## API Reference

### BitcoinTracker Class

```python
from bitcoin_tracker import BitcoinTracker

# Initialize with config
tracker = BitcoinTracker(config_path="config.json")

# Get single address balance
balance = tracker.get_balance("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
print(f"Balance: {balance['balance']}")

# Get all configured addresses
balances = tracker.get_balances()

# Get transaction history
history = tracker.get_transaction_history("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

# Get server information
info = tracker.get_server_info()
```

### Key Methods

- `get_balance(address)`: Get balance for single address
- `get_balances()`: Get balances for all configured addresses
- `get_transaction_history(address)`: Get transaction history
- `get_server_info()`: Get connected server information
- `monitor_continuous()`: Start continuous monitoring

### Return Format

```python
{
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "balance": "50.00000000 BTC",
    "confirmed": Decimal("50.00000000"),
    "unconfirmed": Decimal("0.00000000"),
    "total": Decimal("50.00000000")
}
```

## Server Discovery Quick Reference

**Essential Commands:**
```bash
# 🚀 Get best servers and save them (recommended for new users)
python bitcoin_tracker.py --discover-servers --save-servers

# 🔄 Update server list periodically (weekly/monthly)  
python bitcoin_tracker.py --update-servers --save-servers

# 📊 Check server health and performance
python bitcoin_tracker.py --show-discovery

# 💰 Normal tracking (auto-discovers if servers fail)
python bitcoin_tracker.py
```

**Configuration for Auto-Discovery:**
```json
{
    "enable_server_discovery": true,
    "max_discovered_servers": 20,
    "timeout": 20
}
```

**Benefits:**
- 🔄 **Zero Downtime**: Automatic failover when servers go offline
- ⚡ **Optimal Speed**: Always connects to fastest available servers  
- 🌐 **Global Coverage**: Access to 100+ Electrum servers worldwide
- 🔧 **No Maintenance**: Server lists update themselves

## Comparison with Bitcoin Core Approach

| Feature | Electrum Servers | Bitcoin Core |
|---------|------------------|--------------|
| Setup Time | Seconds | Hours/Days |
| Storage Required | <1 MB | 15-600 GB |
| Initial Sync | None | 1-3 days |
| Ongoing Maintenance | None | Regular updates |
| Privacy | Limited | Full |
| Dependencies | Python only | Bitcoin Core + Python |
| Internet Dependency | High | Medium |

## Examples

### Track Multiple Addresses

```python
from bitcoin_tracker import BitcoinTracker

tracker = BitcoinTracker()
balances = tracker.get_balances()

for balance in balances:
    print(f"{balance['address']}: {balance['balance']}")
```

### Custom Server Configuration

```python
import json

config = {
    "electrum_servers": ["electrum.hsmiths.com:50002"],
    "use_ssl": True,
    "addresses": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],
    "timeout": 15
}

with open("custom_config.json", "w") as f:
    json.dump(config, f, indent=2)

tracker = BitcoinTracker("custom_config.json")
```

### Error Handling

```python
balance = tracker.get_balance("invalid_address")
if "Error" in balance["balance"]:
    print(f"Error: {balance['balance']}")
else:
    print(f"Valid balance: {balance['balance']}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: This README
- **Electrum Protocol**: [ElectrumX Documentation](https://electrumx.readthedocs.io/)

## Changelog

### v2.1.0 (Latest)
- **🆕 NEW**: Automatic Electrum server discovery
- **🆕 NEW**: Health monitoring and server scoring
- **🆕 NEW**: Automatic failover when servers go offline
- **🆕 NEW**: Parallel server testing for faster discovery
- **🆕 NEW**: Command line options for server management
- **ENHANCED**: Improved connection reliability and speed
- **ENHANCED**: Better error handling and retry logic

### v2.0.0
- **BREAKING**: Switched from Bitcoin Core to Electrum servers
- **NEW**: No local Bitcoin node required
- **NEW**: Instant setup and tracking
- **NEW**: Multiple Electrum server support
- **NEW**: Transaction history support
- **NEW**: Server information display
- **REMOVED**: Bitcoin Core dependency
- **REMOVED**: Blockchain sync requirement

### v1.0.0
- Initial release with Bitcoin Core support 