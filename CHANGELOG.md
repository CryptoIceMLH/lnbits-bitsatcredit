# Changelog

All notable changes to BitSatCredit extension will be documented in this file.

## [1.6.0] - 2025-01-30

### Added - Public Page Hero Header
- **Welcome Header**: Added prominent "Welcome to BitSatRelay" hero section at top of public page
- **Subtitle**: "BTC and Nostr Off-Grid Satellite Relay System" tagline for clarity

### Changed - Public Page
- **Enhanced Relay URL Display**: Increased relay URL from body2 to h6 (heading size) with bold weight
- **Larger Copy Button**: Changed copy button from sm to md size for better usability
- **Bolder Label**: "Nostr Relay:" label upgraded to subtitle1 with medium weight

### Fixed - Critical Bug
- **Prevent Spam Account Creation**: Fixed `/api/v1/user/{npub}/balance` and `/api/v1/user/{npub}/can-spend` endpoints that were auto-creating user accounts with 0 balance
- **Read-Only User Checks**: Changed endpoints to use `get_user()` instead of `get_or_create_user()`, preventing spam accounts from scripts checking user balances
- Balance endpoint now returns 404 if user doesn't exist (user must top up first)
- Can-spend endpoint returns `can_afford: false` for non-existent users without creating accounts

### Technical
- Only `/api/v1/topup` endpoint should create new users (when they actually pay and top up)
- Relay scripts now properly check existing users without side effects

## [1.5.3] - 2025-01-30

### Changed - Public Page
- **Enhanced Nostr Relay Display**: Increased relay URL text size from caption to body2 with medium weight for better visibility
- **Improved Copy Button**: Changed copy button size from xs to sm for easier interaction
- **Removed Branding**: Hidden LNbits-Umbrel header link to prevent navigation to root directory

### Fixed
- **GitHub Link Display**: Replaced Quasar icon components with simple emoji links to fix text spacing issues

## [1.5.2] - 2025-01-30

### Added - Admin Dashboard
- **Memo/Notes System**: Admin can now add private notes for each user (not visible to users)
- **Bulk Operations**: Select multiple users and add credits to them at once
- **Select All Checkbox**: Quick selection of all users in the table
- **Configurable Pricing**: Price per message can now be configured via admin UI (stored in database)
- **Memo Column**: Added memo column to user table with inline edit button

### Added - Public Page
- **Improved UI Layout**:
  - Removed experimental warning banner
  - System status shown as small badge with Nostr relay info at top
  - Compact design with dense inputs and reduced padding
  - Better heading hierarchy (main title is bolder)
- **Quick Top-Up Amounts**: Changed from 5/10/100 to 5k/10k/25k/50k/100k sats
- **Memo Field**: Users can add optional memo when topping up
- **Dynamic Pricing**: Price per message loaded from API and displayed to users
- **Educational Content**:
  - "What is BitSatRelay?" section explaining freedom communications use cases
  - Clean GitHub repository links
- **Reorganized Layout**: Balance/Pricing/Stats combined at top, How-To at bottom

### Added - Backend
- **User Memo API**: New endpoint to set/update admin notes for users
- **Price Settings API**: Get and set price per message (admin only)
- **Database Migration**: m006 adds memo column to users table and price_per_message setting

### Technical
- Idempotent migrations with try/except blocks for upgrade safety
- All new API endpoints properly protected with admin authentication
- Price setting stored in system_settings table for runtime configuration

## [1.3.4] - 2024

Initial stable release with core functionality.
