<!-- Updated: 2026-03-09 | Session: 6aeb3c94 -->

# Codebase: Antigravity Autopilot

## Entry Point
`extension/extension.js` — exports `activate()` and `deactivate()`.

## Module Map

| Module | Location | Purpose |
|--------|----------|---------|
| Extension core | `extension/extension.js` | CDP, injection engine, all 5 features, status bar |
| Package manifest | `extension/package.json` | Metadata, 3 commands, 8 settings |
| VSIX manifest | `extension.vsixmanifest` | Package identity, extensionKind: ui |

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `ws` | ^8.14.0 | WebSocket client for CDP |

## Settings

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `autopilot.enabled` | boolean | `true` | Auto-start on activation |
| `autopilot.cdpPort` | number | `0` | Custom CDP port (0 = auto-detect) |
| `autopilot.autoRetry` | boolean | `true` | Click retry on errors |
| `autopilot.autoContinue` | boolean | `true` | Click continue on pauses |
| `autopilot.autoRun` | boolean | `false` | Approve safe commands (opt-in) |
| `autopilot.runBlocklist` | array | see code | Patterns to never auto-approve |
| `autopilot.rateLimitHandler` | boolean | `true` | Auto-wait and retry on rate limits |
| `autopilot.showStats` | boolean | `true` | Show action counts in tooltip |

## Commands
- `autopilot.start` — Start all enabled features
- `autopilot.stop` — Stop and clean up
- `autopilot.stats` — Show detailed session stats

## Conventions
- Status bar is read-only (no click command).
- Extension runs on UI side (`extensionKind: ["ui"]`).
- Version aligned across `package.json` and `extension.vsixmanifest`.
- Config read via `getConfig()` helper; script built dynamically via `buildInjectionScript(config)`.
