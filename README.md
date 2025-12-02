# BitSatCredit - LNbits Extension

https://lnbits.molonlabe.holdings/bitsatcredit/6e1faaf6356b43029124fdeb5f93a297

---

## 🔗 Related Repositories - Integrated System

This is part of a three-component integrated system. Each repository handles a different part of the BitSatRelay network:

| Repository | Purpose | Description |
|------------|---------|-------------|
| **[BitSatRelay](https://github.com/CryptoIceMLH/BitSatRelay)** | Terminal-HQ Bridge | Main codebase - Nostr to satellite bridge |
| **[BitSatRelay-Ground-Station](https://github.com/CryptoIceMLH/BitSatRelay-Ground-Station)** | Off-Grid Terminals | Terminal-1 kits for off-grid satellite TX/RX |
| **[lnbits-bitsatcredit](https://github.com/CryptoIceMLH/lnbits-bitsatcredit)** | Payment System | LNbits extension for Lightning micropayments (this repo) |

**All three components work together** to create the complete BitSatRelay network.

---

## 💜 Support This Project

If you wish to support my work you can donate with BTC:

⚡ **BTC Lightning**: `cryptoice@walletofsatoshi.com`

⚡ **BTC Onchain**: `347ePgUhyvztUWVZ4YZBmBLgTn8hxUFNeQ`

---

## Features

- **User Account Management**: Track user balances by Nostr npub (users created only when they top up)
- **Lightning Payments**: Generate invoices and automatically credit users
- **Transaction History**: Complete audit trail of deposits and spends
- **REST API**: Simple API for BitSatRelay to check/spend credits
- **Public Top-Up Page**: Users can top up credits and view balances
- **Admin Dashboard**: Manage users, view stats, and control system status
- **System Status Toggle**: Control online/offline status with custom maintenance messages
- **Automatic Payment Processing**: Payment listener credits users instantly

## Installation

### Via LNbits Extension Manager

1. Open your LNbits instance
2. Go to **Manage Extensions**
3. Click **Install Extension**
4. Enter repository URL:
   ```
   https://github.com/CryptoIceMLH/lnbits-bitsatcredit
   ```
5. Click **Install**

### Manual Installation

1. Clone this repository into your LNbits extensions directory:
   ```bash
   cd /path/to/lnbits/lnbits/extensions
   git clone https://github.com/CryptoIceMLH/lnbits-bitsatcredit.git bitsatcredit
   ```

2. Restart LNbits:
   ```bash
   poetry run lnbits
   ```

### Upgrading

To upgrade to a new version:
1. Uninstall the current extension from LNbits
2. Reinstall using the latest release from GitHub
3. Database migrations will run automatically

## API Endpoints

### User Management (Public)

- `GET /api/v1/user/{npub}` - Get or create user (creates if doesn't exist)
- `GET /api/v1/user/{npub}/balance` - Check balance (read-only, doesn't create user)
- `GET /api/v1/user/{npub}/transactions` - Get transaction history

### Credit Operations (Public)

- `GET /api/v1/user/{npub}/can-spend?amount=X` - Check if user can afford amount
- `POST /api/v1/user/{npub}/spend?amount=X&memo=Y` - Deduct credits (called by relay script)

### Top-Up (Public)

- `POST /api/v1/topup?wallet_id=XXX` - Generate Lightning invoice (no auth required)
  ```json
  {
    "npub": "npub1...",
    "amount_sats": 100
  }
  ```

### System Status (Public)

- `GET /api/v1/system/status` - Get current system status (online/offline)

### Admin Endpoints (Requires Auth)

- `GET /api/v1/users` - List all users
- `GET /api/v1/transactions/recent` - Recent transactions across all users
- `GET /api/v1/stats` - System-wide statistics
- `POST /api/v1/admin/add-credits` - Manually add credits to user
- `DELETE /api/v1/admin/user/{npub}` - Delete user and all records
- `POST /api/v1/admin/system/status` - Set system online/offline status

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

### System Settings Table (v1.2.1+)
- `key` (PRIMARY KEY) - Setting key
- `value` - Setting value
- `updated_at` - Last updated timestamp

## Usage with BitSatRelay

BitSatRelay relay script uses this extension as its credit system:

```python
from bitsatcredit_client import BitSatCreditClient

# Initialize client
client = BitSatCreditClient(
    extension_url="https://your-lnbits-url/bitsatcredit"
)

# Check if user exists and has balance (read-only, doesn't create user)
user = client.get_user("npub1...")
if not user:
    print("User not found - they need to top up first")
    return

# Check if user can afford message
if client.can_spend("npub1...", amount=1):
    # Deduct credits for message send
    client.spend_credits("npub1...", amount=1, memo="Satellite message")
else:
    print("Insufficient balance")
```

## System Flow

### User Creation
- **Users are ONLY created when they top up for the first time**
- The relay script is read-only - it checks balances but never creates users
- This prevents orphaned 0-balance user records

### Payment Flow

1. User visits public top-up page
2. User enters their npub and amount to top up
3. Extension generates Lightning invoice
4. User pays invoice
5. **Extension payment listener automatically credits user account**
6. User account is created if it doesn't exist

### Message Send Flow

1. User posts message to Nostr relay
2. BitSatRelay relay script receives message
3. Relay checks if user exists and has sufficient balance
4. If balance exists, relay deducts 1 sat and broadcasts message to satellite
5. If no balance, message is rejected
6. Transaction history is recorded

### System Status Control

1. Admin toggles system status on admin page
2. Status is stored in database
3. Public top-up page shows green "ONLINE" or red "OFFLINE" banner
4. Optional custom maintenance message displayed to users
5. **Note**: Actual message processing is controlled by starting/stopping the relay script

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
