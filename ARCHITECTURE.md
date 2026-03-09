<!-- Updated: 2026-03-09 | Session: e82eba9a -->

# Architecture: Antigravity Autopilot

## Stack
- **Runtime**: VS Code Extension API (Node.js)
- **Protocol**: Chrome DevTools Protocol (CDP) via WebSocket (`ws` package)
- **Target**: Antigravity IDE (Electron/VS Code fork)

## Project Structure
```
├── extension.vsixmanifest    # VSIX package manifest
├── [Content_Types].xml       # VSIX content types
├── README.md                 # User-facing documentation
└── extension/
    ├── package.json          # Extension manifest (commands, 8 settings, version)
    ├── extension.js          # Core: CDP connection, multi-feature injection engine
    ├── LICENSE.txt
    └── node_modules/ws/      # WebSocket dependency
```

## Key Decisions
- **CDP over DOM**: Agent panel runs inside the workbench DOM (DIV containers); CDP required for script injection.
- **extensionKind: ui**: Forces local execution for Remote SSH compatibility.
- **Single injection script**: All features bundled as one configurable script; config object passed at injection time.
- **Safety-first Auto-Run**: Opt-in (default off), command text inspected against configurable blocklist before approval.
- **Manual VSIX packaging**: Uses `zip` instead of `vsce` for simplicity.

## Patterns
- **Multi-window broadcast**: Injects into all valid CDP targets.
- **Idempotent injection**: `window.__autopilotInjected` guard.
- **Cooldown**: 2.5s between clicks to prevent duplicates.
- **Stat polling**: Extension polls injected script for action counts every 5s.
