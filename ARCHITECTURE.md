# Architecture: Antigravity Autopilot

## Approach

Direct file patching of Antigravity's bundled JS. No extension, no CDP, no runtime dependency. Two layers:

1. **Source-level auto-retry** — regex rewrites of error switch-case branches
2. **DOM autopilot injection** — IIFE appended to workbench JS for button polling

## What Gets Patched

```
<install_root>/resources/app/out/vs/workbench/workbench.desktop.main.js
  → case patches (retryable, generic)
  → autopilot DOM script (continue, run, ratelimit)

<install_root>/resources/app/out/jetskiAgent/main.js
  → case patches only (retryable, generic)
```

## Layer 1: Case-Level Auto-Retry

Structure-based regex finds `case "retryable"` and `case "generic"` switch branches in minified JS. Captures the full notification object (including `primaryAction.onClick()` binding) and replaces each branch with:

```js
case "retryable": {
  let __agAutoRetryNotification = ORIGINAL_NOTIFICATION_OBJECT;
  if (!globalThis.__agAutoRetryIds) globalThis.__agAutoRetryIds = new Set();
  if (!globalThis.__agAutoRetryIds.has(__agAutoRetryNotification.id)) {
    globalThis.__agAutoRetryIds.add(__agAutoRetryNotification.id);
    return setTimeout(() => {
      __agAutoRetryNotification.primaryAction.onClick();
    }, 500), void 0;
  }
  return __agAutoRetryNotification;
}
```

Resilient because it matches on:
- Literal case labels (`"retryable"`, `"generic"`)
- Notification structure (`id`, `primaryAction`, `secondaryAction`)
- Primary action label strings (`"Try again"`, `"Retry"`, `"Continue"`)

Not dependent on: minified variable names, message factories, button constructors.

## Layer 2: DOM Autopilot Script

A self-contained IIFE appended to `workbench.desktop.main.js`, delimited by sentinel comments:

```
/* __ANTIGRAVITY_AUTOPILOT_START__ */
;(function(){ ... })();
/* __ANTIGRAVITY_AUTOPILOT_END__ */
```

The script:
- Waits 3s after DOM ready for UI initialization
- Polls the agent panel every 1.5s
- Targets both iframe (`antigravity.agentPanel`) and DIV (`antigravity.agentViewContainerId`) layouts
- Checks buttons against text lists (multi-language: English + Italian)
- Click cooldown: 2.5s between actions
- Priority: rate-limit → retry → continue → run

### Agent panel detection

```
iframe#antigravity.agentPanel → contentDocument  (legacy)
div#antigravity.agentViewContainerId → document   (current)
fallback → document
```

### Rate limit handling

Scans body text for patterns like "rate limit", "too many requests", "try again in N seconds". Parses wait duration via regex, defaults to 15s if unparseable. Blocks all polling during wait, then auto-retries.

### Auto-run safety

Off by default. When enabled, inspects text in nearby `pre`/`code`/Monaco elements before clicking. Matches against configurable blocklist. Blocked commands are logged to console.

## Configuration

Baked into the injected script at patch time via CLI flags:

```
--no-retry        disable case-level patches
--no-continue     disable auto-continue
--enable-run      enable auto-run (default off)
--no-ratelimit    disable rate limit handler
--run-blocklist   override blocked command patterns
```

Re-patching with different flags replaces the previous injection (sentinel-based).

## Backup Strategy

- First patch: creates `<file>.bak`
- App update detected (file changed, fully unpatched, no injection, differs from backup): refreshes `.bak`
- `--restore` copies `.bak` back, removing all patches
