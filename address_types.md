# Bitcoin Address Types Supported

## Complete Address Type Support

The Bitcoin Balance Tracker now supports **ALL** major Bitcoin address types:

### 1. **P2PKH (Legacy)** 
- **Format**: Starts with `1`
- **Example**: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
- **Features**: Original Bitcoin address format from 2009
- **Usage**: 43% of Bitcoin supply, decreasing popularity
- **Fees**: Highest transaction fees (legacy format)

### 2. **P2SH (Script Hash)**
- **Format**: Starts with `3` 
- **Example**: `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`
- **Features**: Enables multisig wallets and smart contracts
- **Usage**: 24% of Bitcoin supply, decreasing popularity
- **Fees**: Lower than P2PKH, higher than SegWit

### 3. **P2WPKH (SegWit)** ⭐ **RECOMMENDED**
- **Format**: Starts with `bc1q`, exactly 42 characters
- **Example**: `bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080`
- **Features**: Lower fees, improved security, transaction malleability fix
- **Usage**: 20% of Bitcoin supply, **increasing popularity**
- **Fees**: ~40% cheaper than legacy addresses

### 4. **P2WSH (SegWit Script)**
- **Format**: Starts with `bc1q`, exactly 62 characters  
- **Example**: `bc1qeklep85ntjz4605drds6aww9u0qr46qzrv5xswd35uhjuj8ahfcqgf6hak`
- **Features**: SegWit version of P2SH for complex scripts
- **Usage**: 4% of Bitcoin supply, growing for DeFi applications
- **Fees**: Lowest for complex transactions

### 5. **P2TR (Taproot)** 🚀 **NEWEST**
- **Format**: Starts with `bc1p`, exactly 62 characters
- **Example**: `bc1pxwww0ct9ue7e8tdnlmug5m2tamfn7q06sahstg39ys4c9f3340qqxrdu9k`
- **Features**: Enhanced privacy, Schnorr signatures, advanced smart contracts
- **Usage**: 0.1% of Bitcoin supply, **rapidly growing**
- **Fees**: Most efficient for complex transactions
- **Special**: Required for Bitcoin Ordinals, BRC-20 tokens, Runes

## Address Type Comparison

| Type | Prefix | Characters | Fees | Privacy | Smart Contracts | Supply % |
|------|--------|------------|------|---------|----------------|----------|
| P2PKH | `1` | 26-34 | Highest | Low | No | 43% |
| P2SH | `3` | 34 | High | Medium | Basic | 24% |
| P2WPKH | `bc1q` | 42 | Low | Medium | No | 20% |
| P2WSH | `bc1q` | 62 | Low | Medium | Advanced | 4% |
| P2TR | `bc1p` | 62 | Lowest | Highest | Most Advanced | 0.1% |

## Recommendations by Use Case

### 💰 **For Maximum Savings**
Use **P2WPKH (SegWit)** - saves ~40% on transaction fees

### 🔒 **For Enhanced Privacy** 
Use **P2TR (Taproot)** - all transactions look identical on-chain

### 🏢 **For Business/Multisig**
Use **P2WSH** or **P2TR** - supports complex spending conditions

### 🎨 **For Bitcoin NFTs/Tokens**
Use **P2TR (Taproot)** - required for Ordinals, BRC-20, Runes

### 🔄 **For Maximum Compatibility**
Use **P2WPKH (SegWit)** - supported by all modern wallets and exchanges

## Your Current Setup

All your addresses are **P2WPKH (SegWit)** - excellent choice! ✅
- Lower transaction fees than legacy formats
- Supported by all modern wallets and exchanges  
- Enhanced security features
- Perfect for regular Bitcoin transactions

