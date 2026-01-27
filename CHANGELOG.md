# Changelog

All notable changes to this project will be documented in this file.

## [3.0.13] - 2026-01-27

### Fixed
- **Optimistic updates for Number entities** – Number sliders now reflect the new value immediately when changed in the UI.
  - `number.py`: added an optimistic cache (`_optimistic_native_value`) and call to `async_write_ha_state()` in `async_set_native_value()` so the slider updates instantly.
  - Clear the optimistic cache on coordinator updates (`_handle_coordinator_update()`), and reconcile with device state after the coordinator refresh.

- **Gas consumption reporting for Energy dashboard**
  - Fixed incorrect use of `device_class: gas` with a flow-rate unit (`m³/h`).
  - Gas flow is now correctly modeled as a **volume flow rate** sensor (`m³/h`).
  - Added a new cumulative **gas usage** sensor (`m³`, `state_class: total_increasing`) derived from the gas flow.
  - The cumulative gas sensor is compatible with Home Assistant **Energy dashboard** and long-term statistics.
  - Gas usage is persisted across restarts using `RestoreEntity`, preventing resets or spikes after reboot.

- **Coordinator update handling**
  - Fixed invalid `async def _handle_coordinator_update()` implementations.
  - `_handle_coordinator_update()` is now synchronous everywhere, as required by `CoordinatorEntity`.
  - Prevents dropped coordinator callbacks, runtime warnings, and entities failing to update.

### Migration notes (3.0.13)

This release fixes gas consumption reporting and improves coordinator handling.

If you previously used the `gasverbruik / gasusage` sensor in the Energy dashboard:
- That sensor represented **gas flow** (`m³/h`) and was never compatible with Energy.
- Energy dashboard now requires the new **`Atag One Gas Used`** sensor (`m³`).

#### What you may need to do
- Open **Settings → Dashboards → Energy**
- Remove the old gas sensor (if configured)
- Select **Atag One Gas Used** as your gas source

No other manual steps are required.  
Existing energy statistics will automatically rebuild over time.


## [3.0.12] - 2026-01-26

### Changed
- **Improved request retry logic in `_async_send_request()`** - Replaced recursive retry mechanism with loop-based approach
  - Configurable `max_attempts` parameter (default: 3)
  - Exponential backoff with configurable base (1s), factor (2x), and max delay (10s)
  - Random jitter (0–250ms) to prevent thundering herd
  - Handles `Retry-After` header for HTTP 429 responses (capped at 30s)
  - Retryable status codes: 408, 425, 429, 500, 502, 503, 504
  - Non-retryable status codes: 400, 401, 403, 404 (fail immediately)
  - Retryable exceptions: `asyncio.TimeoutError`, `aiohttp.ClientError`
  - Always re-raises `asyncio.CancelledError` immediately
  - Enhanced debug logging per attempt without payload exposure

### Fixed
- **Eliminated duplicate state updates** - Removed redundant `async_write_ha_state()` calls in entity update methods
  - Removed from `number.py` (`async_set_native_value()`)
  - Removed from `switch.py` (`async_turn_on()` and `async_turn_off()`)
  - Removed from `select.py` (`async_select_option()`)
  - Removed from `climate.py` (`async_set_hvac_mode()`, `async_set_preset_mode()`, `async_set_temperature()`)
  - This prevents excessive state change activity log entries when values haven't actually changed
  - The `DataUpdateCoordinator` now naturally handles state updates without duplication

## [3.0.11] - 2026-01-26

### Changed
- Options flow class now inherits a base class for better code organization

## [3.0.10] - 2026-01-25

### Fixed
- Version bump in manifest.json

## [3.0.9] - 2026-01-24

### Fixed
- Various fixes and improvements
- Added translations support

## [3.0.8] - 2026-01-23

### Fixed
- UnitOfTemperature constant fix for Home Assistant compatibility

## [3.0.7] - 2026-01-22

### Fixed
- Discovery fix when Atag One device is not found on the network

### Changed
- Removed error logging in non-critical scenarios

## [3.0.6] - 2026-01-20

### Added
- Dutch (NL) translation support

### Fixed
- Gas consumption now displays correct value
- Discovery of IP address now available in config flow
- Code cleanup and refactoring

## [3.0.5] - 2026-01-15

### Added
- Implemented vacation temperature slider control
- Fixed issue with eco temperature slider

## [3.0.4] - 2026-01-10

### Fixed
- Various bug fixes and improvements

## [3.0.3] - 2026-01-05

### Fixed
- Removed error logging for cleaner operation

### Changed
- Typo fixes in configuration options (e.g., `wdr_temps_influence`)

## [3.0.2] - 2025-12-28

### Added
- New features and platform support

## [3.0.1] - 2025-12-20

### Initial Release
- Full support for ATAG One thermostat
- Climate entity for temperature control
- Sensors for various device metrics
- Number entities for calibration
- Switch entities for device control
- Select entities for configuration options
- Multi-language support (EN, DE, FR, NL)
- Config flow for easy setup
- Discovery support for automatic device detection

---

## Format

This changelog follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

### Categories
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Fixed** - Bug fixes
- **Removed** - Removed functionality
- **Deprecated** - Soon-to-be removed functionality
- **Security** - Security fixes and improvements
