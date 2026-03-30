# Changelog

## [3.0.0] - 2026-03-30

### Changed
- **Complete rewrite**: replaced CDP-based VS Code extension with direct file patching.
- No longer requires `--remote-debugging-port` or any extension install.
- Works across all Antigravity instances, accounts, and environments simultaneously.

### Added
- `patch_antigravity.py` — main patching script (Python 3, zero dependencies).
- `patch_antigravity.sh` — Linux launcher.
- `patch_antigravity.cmd` — Windows launcher.
- **Two-layer patching**:
  - Source-level: structure-based regex patches on `retryable`/`generic` switch branches for auto-retry.
  - DOM-level: self-contained autopilot IIFE injected into workbench JS for auto-continue, auto-run, rate limit handling.
- Feature toggles via CLI: `--no-retry`, `--no-continue`, `--enable-run`, `--no-ratelimit`, `--run-blocklist`.
- Linux install auto-detection (system packages, snap, flatpak, local installs).
- `--all` flag to patch every detected installation at once.
- `--check` mode to verify patch status without modifying files.
- `--restore` to revert to original files from backup.
- Sentinel-based injection tracking — re-patching cleanly replaces previous injection.
- Automatic backup refresh when Antigravity updates.

### Removed
- VS Code extension (CDP/WebSocket approach was unreliable — port conflicts, didn't work across multiple instances or separate environments).
- `ws` npm dependency.
- VSIX packaging.

## [2.0.2] - 2026-03-09

### Fixed
- Agent panel detection: supports DIV-based layout with iframe fallback.

## [2.0.1] - 2026-03-09

### Fixed
- CDP connection retries with exponential backoff.

## [2.0.0] - 2026-03-09

### Changed
- Renamed from Antigravity Auto-Retry to Antigravity Autopilot.
- Added auto-continue, auto-run, rate limit handler, session stats.
- CDP-based VS Code extension approach.

## [1.0.0] - Initial release
- CDP-based auto-retry with multi-window support.
