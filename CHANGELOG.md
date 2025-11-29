# Changelog

All notable changes to the BitSatCredit LNbits extension will be documented in this file.

## [v1.5.1] - 2025-11-29

### Fixed
- Fixed migration m006 to use INSERT OR IGNORE to prevent duplicate key errors
- Updated config.json version number to match release version

---

## [v1.5.0] - 2025-11-29

### Added - Admin Dashboard
- **Configurable Pricing**: Price per message is now configurable via admin settings (no longer hardcoded at 1 sat)
- **User Memos**: Admins can add private notes/memos to user accounts for internal reference
- **Bulk Operations**:
  - "Select All" checkbox to select all filtered users at once
  - Bulk add credits feature to give free credits to multiple users simultaneously
- **Table Sorting**: Fixed sortable columns - arrows now properly sort users by any field
- **Enhanced User Management**: Memo column added to user table with inline edit functionality

### Added - Public User Page
- **Quick Top-Up Amounts**: Changed quick amount buttons from 5/10/100 to 5k/10k/25k/50k/100k sats
- **User Memo Field**: Users can now add optional memos/notes when making top-up payments
- **Dynamic Pricing Display**: Price per message now loads from API and updates when admin changes it
- **Information Sections**:
  - "What is BitSatRelay?" - Explains the mission of uncensorable communications for off-grid, emergencies, natural disasters, and civil unrest scenarios
  - "Open Source" section with links to software and hardware repositories
- **Compact UI Design**:
  - Removed large orange "EXPERIMENTAL PLATFORM" warning box
  - System status changed to small badge indicator (no longer full-width banner)
  - Reduced padding and spacing throughout (dense inputs, smaller cards)
  - Fixed heading hierarchy - main title now bolder than section titles
  - Reorganized layout: Balance/Pricing at top, How-To at bottom
  - Combined Stats, Pricing, and System Status into unified sections

### Changed - Backend
- **Models**: Added `memo` field to User model for admin notes
- **API Endpoints**:
  - `GET /api/v1/settings/price` - Public endpoint to fetch current price per message
  - `POST /api/v1/admin/settings/price` - Admin endpoint to update price per message
  - `POST /api/v1/admin/user/{npub}/memo` - Admin endpoint to set user memos
- **Database**: New `memo` column in users table (requires migration)

### Technical Details
- Price per message stored in `system_settings` table as key-value pair
- User memos are searchable via admin user filter
- Bulk operations process users sequentially with proper error handling
- All UI changes maintain Vue 3 + Quasar framework patterns

### Migration Required
Run this SQL to add the memo field:
```sql
ALTER TABLE bitsatcredit.users ADD COLUMN memo TEXT DEFAULT NULL;
```

### Repository Links
- Software: https://github.com/CryptoIceMLH/lnbits-bitsatcredit
- Hardware: https://github.com/CryptoIceMLH/BitSatRelay-Ground-Station

---

## [v1.3.4] - Previous Release
See: https://github.com/CryptoIceMLH/lnbits-bitsatcredit/releases/tag/v1.3.4
