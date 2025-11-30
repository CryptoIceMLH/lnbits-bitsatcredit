# Changelog

All notable changes to BitSatCredit extension will be documented in this file.

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
