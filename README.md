# Bitcoin Balance Tracker

A lightweight Python application that tracks Bitcoin wallet balances using public Electrum servers. **No local Bitcoin node required!** Simply configure your addresses and start tracking instantly.

## Features

- **No Bitcoin Node Required**: Uses public Electrum servers - no setup, no storage, no syncing
- **Instant Setup**: Start tracking addresses in seconds
- **Multiple Address Support**: Monitor multiple Bitcoin addresses simultaneously
- **Real-time Balance Updates**: Get current balances including unconfirmed transactions
- **Multiple Server Support**: Automatically connects to available Electrum servers
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
    "timeout": 20
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

- `--address ADDRESS`: Track specific address
- `--continuous`: Run in continuous mode with periodic updates
- `--config PATH`: Use custom config file path
- `--history`: Show transaction history for address
- `--server-info`: Display connected server information

## Configuration

### Config File Options

| Option | Description | Default |
|--------|-------------|---------|
| `electrum_servers` | List of Electrum servers (host:port) | Multiple servers |
| `use_ssl` | Use SSL/TLS connections | true |
| `addresses` | List of Bitcoin addresses to track | [] |
| `update_interval` | Update interval in seconds for continuous mode | 60 |
| `timeout` | Connection timeout in seconds | 20 |

### Supported Address Types

- **P2PKH**: Legacy addresses starting with '1' (e.g., 1A1zP1eP...)
- **P2SH**: Script addresses starting with '3' (e.g., 3J98t1W...)
- **P2WPKH**: Bech32 addresses starting with 'bc1' (limited support)

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