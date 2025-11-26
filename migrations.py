# the migration file is where you build your database tables
# If you create a new release for your extension ,
# remember the migration file is like a blockchain, never edit only add!

empty_dict: dict[str, str] = {}


async def m001_users(db):
    """User accounts table"""
    await db.execute(
        f"""
        CREATE TABLE bitsatcredit.users (
            npub TEXT PRIMARY KEY,
            balance_sats INTEGER NOT NULL DEFAULT 0,
            total_spent INTEGER NOT NULL DEFAULT 0,
            total_deposited INTEGER NOT NULL DEFAULT 0,
            message_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )


async def m002_transactions(db):
    """Transaction history"""
    await db.execute(
        f"""
        CREATE TABLE bitsatcredit.transactions (
            id TEXT PRIMARY KEY,
            npub TEXT NOT NULL,
            type TEXT NOT NULL,
            amount_sats INTEGER NOT NULL,
            payment_hash TEXT,
            memo TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            FOREIGN KEY (npub) REFERENCES users(npub)
        );
        """
    )


async def m003_topup_requests(db):
    """Top-up invoice tracking"""
    await db.execute(
        f"""
        CREATE TABLE bitsatcredit.topup_requests (
            id TEXT PRIMARY KEY,
            npub TEXT NOT NULL,
            amount_sats INTEGER NOT NULL,
            payment_hash TEXT NOT NULL UNIQUE,
            bolt11 TEXT NOT NULL,
            paid BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            paid_at TIMESTAMP,
            FOREIGN KEY (npub) REFERENCES users(npub)
        );
        """
    )


async def m004_satellite_messages(db):
    """Satellite message tracking (optional)"""
    await db.execute(
        f"""
        CREATE TABLE bitsatcredit.satellite_messages (
            id TEXT PRIMARY KEY,
            filename TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            original_npub TEXT,
            satellite_timestamp TEXT,
            nostr_event_id TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )
