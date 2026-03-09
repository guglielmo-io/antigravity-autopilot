<!-- Updated: 2026-03-09 | Session: 6aeb3c94 -->

# Changelog

## [2.0.0] - 2026-03-09

### Renamed
- **Antigravity Auto-Retry** → **Antigravity Autopilot**
- New command namespace: `autopilot.*`

### Added
- **Auto-Continue**: Clicks Continue/Proceed/Yes when agent pauses mid-generation.
- **Auto-Run**: Opt-in safe command approval. Inspects commands against configurable blocklist before clicking Run.
- **Rate Limit Handler**: Detects rate limit messages, waits the required duration, then auto-retries.
- **Session Stats**: Tracks action counts (retries, continues, runs, rate waits) per session. Displayed in status bar tooltip.
- **8 configurable settings**: Every feature independently toggleable.

### Changed
- Injection script rebuilt as configurable multi-feature engine.
- Config object passed at injection time via `buildInjectionScript()`.
- Stat polling every 5s from CDP for live tooltip updates.
- README rewritten with full feature docs, safety section, updated architecture diagram.

### Fixed (from 1.1.0)
- Status bar is read-only indicator (no click command).
- CDP port configurable via `autopilot.cdpPort` setting.
- `extensionKind: ["ui"]` for Remote SSH compatibility.

## [1.0.0] - Initial release
- CDP-based auto-retry with multi-window support.
- Multi-language retry button detection.
- Status bar indicator.
