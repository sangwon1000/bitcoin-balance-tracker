# Bitcoin Balance Tracker API

A clean, simple REST API for tracking Bitcoin wallet balances. Perfect for single-website integration with your Bitcoin balance tracker.

## 🚀 Features

- **Simple API Key Authentication** - Just add your API key to requests
- **All Bitcoin Address Types** - Legacy, SegWit, Taproot support
- **Rate Limiting** - Built-in protection against abuse
- **Comprehensive Validation** - Input validation and error handling
- **Auto Documentation** - Interactive Swagger/OpenAPI docs
- **HTTPS Ready** - Production-ready security
- **Comprehensive Logging** - Full audit trail

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Important**: Change the `API_KEY` in your `.env` file!

### 3. Start the API

```bash
# Development
python api/main.py

# Production with Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 4. View Documentation

Open http://localhost:8000/v1/docs for interactive API documentation.

## 🔐 Authentication

All endpoints require an API key passed in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/v1/bitcoin/balance/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

### JavaScript Example

```javascript
const API_BASE = 'http://localhost:8000/v1';
const API_KEY = 'your-api-key';

async function getBitcoinBalance(address) {
    const response = await fetch(`${API_BASE}/bitcoin/balance/${address}`, {
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data; // Balance data
}

// Usage
getBitcoinBalance('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    .then(balance => console.log('Balance:', balance))
    .catch(error => console.error('Error:', error));
```

## 📚 API Endpoints

### Bitcoin Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/bitcoin/balance/{address}` | Get address balance |
| `POST` | `/v1/bitcoin/balances` | Get multiple address balances |
| `GET` | `/v1/bitcoin/history/{address}` | Get transaction history |
| `POST` | `/v1/bitcoin/validate` | Validate Bitcoin address |
| `GET` | `/v1/bitcoin/server-info` | Get Electrum server info |
| `POST` | `/v1/bitcoin/discover-servers` | Discover healthy servers |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (no auth required) |
| `GET` | `/v1/status` | API status |
| `GET` | `/v1/docs` | Interactive documentation |

## 📖 API Usage Examples

### Get Address Balance

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8000/v1/bitcoin/balance/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

Response:
```json
{
  "success": true,
  "message": "Balance retrieved successfully",
  "data": {
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "confirmed_balance": "50.00000000",
    "unconfirmed_balance": "0.00000000",
    "total_balance": "50.00000000",
    "address_type": "P2PKH",
    "last_updated": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Get Multiple Balances

```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
      "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    ]
  }' \
  http://localhost:8000/v1/bitcoin/balances
```

### Get Transaction History

```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/v1/bitcoin/history/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?limit=10&offset=0"
```

### Validate Address

```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"}' \
  http://localhost:8000/v1/bitcoin/validate
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | **Required** - Your API authentication key | - |
| `ENVIRONMENT` | Environment (development/production) | development |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | localhost:3000,... |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | Rate limit per minute | 120 |
| `BITCOIN_CONFIG_PATH` | Path to Bitcoin tracker config | config.json |
| `LOG_LEVEL` | Logging level | INFO |

### Rate Limiting

- **120 requests per minute** by default
- **20 burst requests** allowed
- Rate limits are per IP address
- Headers included in responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Security Features

- **API Key Authentication** - All endpoints protected
- **HTTPS Enforcement** - In production mode
- **CORS Protection** - Configurable allowed origins
- **IP Allowlisting** - Optional IP restrictions
- **Input Validation** - Comprehensive request validation
- **Security Headers** - OWASP-compliant security headers
- **Rate Limiting** - Protection against abuse

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Set production environment
export ENVIRONMENT=production
export API_KEY=your-very-secure-production-key
export CORS_ORIGINS=https://yourwebsite.com
export HOST=0.0.0.0
export PORT=8000
```

### 2. SSL/HTTPS Setup

```bash
# Add SSL certificate paths
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
```

### 3. Run with Gunicorn

```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 4. Nginx Reverse Proxy (Recommended)

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00",
  "services": {
    "api": "healthy",
    "bitcoin_tracker": "healthy",
    "electrum_connection": "healthy"
  }
}
```

### Logs

Logs are written to stdout by default. In production, configure log rotation:

```bash
# Log to file
export LOG_FILE=/var/log/bitcoin-api.log

# Or use systemd journal
journalctl -u bitcoin-api -f
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Test with coverage
pytest --cov=api
```

### Example Test

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_balance_requires_auth():
    response = client.get("/v1/bitcoin/balance/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    assert response.status_code == 401

def test_balance_with_auth():
    headers = {"X-API-Key": "your-api-key"}
    response = client.get("/v1/bitcoin/balance/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", headers=headers)
    assert response.status_code == 200
```

## 🔧 Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check your API key is correct and included in headers
2. **429 Rate Limited**: You're making too many requests, wait before retrying
3. **503 Service Unavailable**: Bitcoin tracker can't connect to Electrum servers
4. **400 Bad Request**: Invalid Bitcoin address format

### Debug Mode

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python api/main.py
```

### Logs Analysis

```bash
# Show recent API logs
tail -f /var/log/bitcoin-api.log

# Filter for errors
grep "ERROR" /var/log/bitcoin-api.log

# Show rate limit hits
grep "Rate limit" /var/log/bitcoin-api.log
```

## 📝 Support

- **Documentation**: `/v1/docs` (Interactive Swagger UI)
- **Health Check**: `/health`
- **Status**: `/v1/status`

## 🔒 Security Best Practices

1. **Use HTTPS in production**
2. **Keep API keys secure** - Never commit to version control
3. **Set up IP allowlisting** if possible
4. **Monitor rate limits** and unusual activity
5. **Keep dependencies updated**
6. **Use environment variables** for configuration
7. **Set up proper logging** and monitoring

## 📄 License

This project is licensed under the MIT License - see the original LICENSE file for details. 