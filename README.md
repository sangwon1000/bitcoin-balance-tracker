# Bitcoin Balance Tracker

A lightweight Python application that tracks Bitcoin wallet balances using a local Bitcoin Core pruned node. This eliminates the need for third-party APIs while keeping storage requirements minimal (~10-15 GB).

## Features

- **Pruned Node Support**: Uses Bitcoin Core pruning to minimize storage (~10-15 GB vs 600+ GB)
- **Local RPC Connection**: Direct connection to Bitcoin Core via RPC
- **Multiple Address Tracking**: Monitor multiple Bitcoin addresses simultaneously
- **Real-time Balance Updates**: Get current balances including unconfirmed transactions
- **Simple Configuration**: Easy setup with config file
- **Cross-platform**: Works on macOS, Linux, and Windows

## Prerequisites

- **Bitcoin Core**: v24.0+ with pruning enabled
- **Python**: 3.8 or higher
- **Storage**: ~15 GB free space (for pruned node)
- **Internet**: Stable connection for initial sync

## Quick Start

### 1. Install Bitcoin Core

Download from [bitcoincore.org](https://bitcoincore.org/) and install.

### 2. Configure Bitcoin Core for Pruning

Create `~/.bitcoin/bitcoin.conf` (Linux/macOS) or `%APPDATA%\Bitcoin\bitcoin.conf` (Windows):

```ini
server=1
rpcuser=your_username
rpcpassword=your_secure_password
rpcport=8332
prune=550
maxconnections=8
dbcache=512
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Tracker

Copy `config.example.json` to `config.json` and update:

```json
{
  "rpc_user": "your_username",
  "rpc_password": "your_secure_password",
  "rpc_host": "localhost",
  "rpc_port": 8332,
  "addresses": [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
  ],
  "update_interval": 60
}
```

### 5. Start Bitcoin Core

```bash
# Start Bitcoin Core daemon
bitcoind -daemon

# Check sync status
bitcoin-cli getblockchaininfo
```

### 6. Run the Tracker

```bash
python bitcoin_tracker.py
```

## Usage

### Basic Usage

```bash
# Track configured addresses
python bitcoin_tracker.py

# Track specific address
python bitcoin_tracker.py --address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Continuous monitoring
python bitcoin_tracker.py --continuous
```

### Command Line Options

- `--address ADDRESS`: Track specific address
- `--continuous`: Run in continuous mode with updates
- `--config PATH`: Use custom config file
- `--verbose`: Enable verbose logging

## Configuration

### Config File Options

| Option | Description | Default |
|--------|-------------|---------|
| `rpc_user` | Bitcoin Core RPC username | - |
| `rpc_password` | Bitcoin Core RPC password | - |
| `rpc_host` | Bitcoin Core RPC host | localhost |
| `rpc_port` | Bitcoin Core RPC port | 8332 |
| `addresses` | List of addresses to track | [] |
| `update_interval` | Update interval in seconds | 60 |

### Bitcoin Core Pruning Settings

| Setting | Description | Recommended |
|---------|-------------|-------------|
| `prune=550` | Keep 550 MB of recent blocks | 550 |
| `maxconnections=8` | Limit peer connections | 8 |
| `dbcache=512` | Database cache in MB | 512 |

## Storage Requirements

- **Full Node**: ~600 GB
- **Pruned Node**: ~10-15 GB
- **Initial Sync**: Downloads full blockchain then prunes

## Performance

- **Sync Time**: 1-3 days (depends on internet speed)
- **CPU Usage**: High during sync, low afterward
- **Memory**: ~1-2 GB during operation
- **Network**: ~500-600 GB initial download

## Troubleshooting

### Common Issues

**RPC Connection Refused**
```bash
# Check if Bitcoin Core is running
bitcoin-cli getblockchaininfo

# Verify RPC credentials in config
```

**Slow Sync**
```bash
# Reduce connections
maxconnections=4

# Increase database cache (if RAM available)
dbcache=1024
```

**Storage Full**
```bash
# Use external drive
datadir=/path/to/external/drive

# Reduce pruning
prune=1000
```

### Logs

Check Bitcoin Core logs:
```bash
tail -f ~/.bitcoin/debug.log
```

## Security

- Keep RPC credentials secure
- Use strong passwords
- Restrict RPC to localhost (default)
- Consider using `rpcbind=127.0.0.1`

## API Reference

### BitcoinTracker Class

```python
from bitcoin_tracker import BitcoinTracker

tracker = BitcoinTracker(config_path="config.json")
balance = tracker.get_balance("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
```

### Methods

- `get_balance(address)`: Get balance for single address
- `get_balances()`: Get balances for all configured addresses
- `monitor_continuous()`: Start continuous monitoring
- `validate_address(address)`: Validate Bitcoin address

## Examples

### Track Single Address

```python
from bitcoin_tracker import BitcoinTracker

tracker = BitcoinTracker()
balance = tracker.get_balance("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
print(f"Balance: {balance} BTC")
```

### Continuous Monitoring

```python
from bitcoin_tracker import BitcoinTracker

tracker = BitcoinTracker()
tracker.monitor_continuous()
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
- **Bitcoin Core**: [bitcoincore.org](https://bitcoincore.org/)

## Changelog

### v1.0.0
- Initial release
- Pruned node support
- Multiple address tracking
- Configuration file support 