-- Migration for BitSatCredit v1.4.0
-- Adds memo column to users table for admin notes

-- Add memo column to users table (NULL is allowed, no default required)
ALTER TABLE bitsatcredit.users ADD COLUMN IF NOT EXISTS memo TEXT;

-- Note: IF NOT EXISTS is PostgreSQL 9.6+
-- For older versions or if this fails, use:
-- ALTER TABLE bitsatcredit.users ADD COLUMN memo TEXT;
