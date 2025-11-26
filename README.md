# BitSatCredit - LNbits Extension

User credit management system for [BitSatRelay](https://github.com/yourusername/btcsatcoms) satellite messaging relay.

## Features

- **User Account Management**: Track user balances by Nostr npub
- **Lightning Payments**: Generate invoices and automatically credit users
- **Transaction History**: Complete audit trail of deposits and spends
- **REST API**: Simple API for BitSatRelay to check/spend credits
- **Web UI**: Users can top up credits and view transaction history
- **Automatic Payment Processing**: Payment listener credits users instantly

## Installation

### Via LNbits Extension Manager

1. Open your LNbits instance
2. Go to **Manage Extensions**
3. Click **Install Extension**
4. Enter repository URL:
   ```
   https://gitlab.com/YOURUSERNAME/bitsatcredit
   ```
5. Click **Install**

### Manual Installation

1. Clone this repository into your LNbits extensions directory:
   ```bash
   cd /path/to/lnbits/lnbits/extensions
   git clone https://gitlab.com/YOURUSERNAME/bitsatcredit.git
   ```

2. Restart LNbits:
   ```bash
   poetry run lnbits
   ```

## API Endpoints

### User Management

- `GET /api/v1/user/{npub}` - Get or create user
- `GET /api/v1/user/{npub}/balance` - Check balance
- `GET /api/v1/user/{npub}/transactions` - Get transaction history

### Credit Operations

- `GET /api/v1/user/{npub}/can-spend?amount=X` - Check if user can afford amount
- `POST /api/v1/user/{npub}/spend?amount=X&memo=Y` - Deduct credits

### Top-Up

- `POST /api/v1/user/{npub}/topup` - Generate Lightning invoice
  ```json
  {
    "npub": "npub1...",
    "amount_sats": 100
  }
  ```

### Health Check

- `GET /api/v1/health` - Check if extension is running

## Database Schema

### Users Table
- `npub` (PRIMARY KEY) - Nostr public key
- `balance_sats` - Current balance
- `total_spent` - Lifetime spending
- `total_deposited` - Lifetime deposits
- `message_count` - Messages sent via satellite
- `created_at`, `updated_at` - Timestamps

### Transactions Table
- `id` (PRIMARY KEY)
- `npub` (FOREIGN KEY)
- `type` - "deposit" or "spend"
- `amount_sats` - Transaction amount
- `payment_hash` - Lightning payment hash (if applicable)
- `memo` - Transaction description
- `created_at` - Timestamp

### TopUp Requests Table
- `id` (PRIMARY KEY)
- `npub` (FOREIGN KEY)
- `amount_sats` - Top-up amount
- `payment_hash` - Lightning invoice payment hash
- `bolt11` - Lightning invoice string
- `paid` - Payment status
- `created_at`, `paid_at` - Timestamps

## Usage with BitSatRelay

BitSatRelay uses this extension as its database and payment system:

```python
from lnbits_extension_client import LNbitsExtensionClient

client = LNbitsExtensionClient(
    base_url="http://your-lnbits-url/bitsatcredit",
    api_key=""  # Optional
)

# Check balance
balance = client.get_user_balance("npub1...")

# Check if user can afford message
can_send = client.can_user_spend("npub1...", amount=1)

# Deduct credits for message send
if can_send:
    client.spend_credits("npub1...", amount=1, memo="Satellite message")

# Generate top-up invoice
invoice = client.generate_topup_invoice("npub1...", amount=100)
print(f"Pay this invoice: {invoice['bolt11']}")
```

## Payment Flow

1. User wants to send satellite message
2. BitSatRelay checks if user has sufficient balance
3. If insufficient, user tops up via Lightning invoice
4. **Extension payment listener automatically credits user**
5. BitSatRelay deducts credits when message is sent
6. Transaction history is recorded

## Configuration

No additional configuration needed. The extension:
- Creates database tables automatically on first run
- Starts payment listener automatically
- Uses LNbits wallet for invoice generation

## Development

### Project Structure
```
bitsatcredit/
├── __init__.py           # Extension initialization
├── config.json           # Extension metadata
├── models.py             # Pydantic data models
├── migrations.py         # Database migrations
├── crud.py               # Database operations
├── services.py           # Business logic
├── views_api.py          # REST API endpoints
├── views.py              # Web UI routes
├── tasks.py              # Payment listener
└── templates/            # HTML templates
```

### Testing

```bash
pytest tests/
```

## License

MIT

## Support

For issues and questions:
- Open an issue on GitLab
- Join the discussion on Nostr

## Credits

Built for the BitSatRelay satellite messaging system.
