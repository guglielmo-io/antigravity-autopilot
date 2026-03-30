<div align="center">

<img src="https://img.shields.io/badge/Antigravity-Autopilot-blueviolet?style=for-the-badge&logo=visual-studio-code&logoColor=white" alt="Antigravity Autopilot" />

# Antigravity Autopilot

### Your AI agent writes the code. Autopilot handles everything else.

**One script. Zero babysitting. Full autonomy for your AI coding agent.**

<br />

[![GitHub Release](https://img.shields.io/github/v/release/guglielmo-io/antigravity-autopilot?style=flat-square&color=success&label=latest)](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE.txt)
[![Stars](https://img.shields.io/github/stars/guglielmo-io/antigravity-autopilot?style=flat-square&color=yellow)](https://github.com/guglielmo-io/antigravity-autopilot/stargazers)
[![Downloads](https://img.shields.io/github/downloads/guglielmo-io/antigravity-autopilot/total?style=flat-square&color=brightgreen)](https://github.com/guglielmo-io/antigravity-autopilot/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/guglielmo-io/antigravity-autopilot/pulls)

<br />

**Auto-Retry** · **Auto-Continue** · **Auto-Run** · **Rate Limit Handler**

<br />

[**Download Latest**](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;[Report Bug](https://github.com/guglielmo-io/antigravity-autopilot/issues)&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;[Request Feature](https://github.com/guglielmo-io/antigravity-autopilot/issues)

</div>

<br />

---

<br />

## Without Autopilot vs With Autopilot

<table>
<tr>
<td width="50%">

### Before

```
Agent fails → you click Retry
Agent pauses → you click Continue
Agent runs a command → you click Approve
Rate limit → you wait → you click Retry
Repeat 50+ times per session.
```

**You're not coding. You're a human click-bot.**

</td>
<td width="50%">

### After

```
Agent fails → patched out at source
Agent pauses → Autopilot clicks Continue
Safe command → Autopilot approves it
Rate limit → Autopilot waits → retries
You keep working on something else.
```

**Your agent runs fully autonomous.**

</td>
</tr>
</table>

<br />

---

<br />

## Four Features. One Script. Zero Clicks.

<br />

### Auto-Retry — Errors intercepted at the source

Not a DOM hack. Not a button click. Autopilot patches the actual error handling branches (`case "retryable"`, `case "generic"`) directly in Antigravity's bundled JS. First failure auto-retries via `primaryAction.onClick()` in 500ms. Second failure on the same notification shows the original popup. **This is as fast and reliable as it gets.**

<br />

### Auto-Continue — No more "Do you want me to continue?"

Long generation stopped halfway? **"Continue"**, **"Proceed"**, **"Yes"**, **"Continua"**, **"Keep Going"** — clicked without you lifting a finger. Chain entire multi-file refactors without touching the keyboard.

<br />

### Auto-Run — Safe commands approved automatically

> **Opt-in and guarded by default.** Disabled until you turn it on.

Agent wants to run `npm install` or `mkdir src`? Approved instantly. Tries `rm -rf /` or `sudo`? **Blocked.** Every command is inspected against a configurable blocklist before approval.

**Default blocklist protects against:**

```
rm -rf · rm -r · sudo · drop · delete · format · mkfs
shutdown · reboot · kill -9 · truncate · dd if= · chmod 777 · chown
```

You control the blocklist. Add patterns, remove patterns, make it yours.

<br />

### Rate Limit Handler — Wait it out, hands-free

Hit a provider rate limit? Autopilot detects it, reads the wait time, counts down silently, and retries the moment the window opens. Works with **"rate limited"**, **"too many requests"**, **"try again in 30s"**, **"quota exceeded"**.

No staring at a timer. No setting reminders. Just results.

<br />

---

<br />

## How It Works

Unlike extension-based approaches that require CDP ports and break with multiple instances, Autopilot **patches Antigravity's bundled files directly**. Two layers:

<br />

### Layer 1 — Source-Level Auto-Retry

Structure-based regex matching finds `case "retryable"` and `case "generic"` switch branches in the minified JS and rewrites them to auto-invoke the existing primary action. Applied to both:

- `resources/app/out/vs/workbench/workbench.desktop.main.js`
- `resources/app/out/jetskiAgent/main.js`

Matches on **case labels and notification object structure** — not minified variable names. Survives routine Antigravity updates where only the bundler renames symbols.

<br />

### Layer 2 — DOM Autopilot

A self-contained script injected at the end of the workbench file. It polls the agent panel every **1.5 seconds**, detects actionable buttons, and clicks them with a **2.5-second cooldown** to prevent double-clicks. Handles continue prompts, safe command approval, and rate limit recovery.

<br />

```
┌──────────────────────────────────────────────────────────────────┐
│                      Antigravity Instance                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  workbench.desktop.main.js  (patched)                    │    │
│  │                                                          │    │
│  │  Layer 1: case "retryable" → auto-retry at source        │    │
│  │           case "generic"   → auto-retry at source        │    │
│  │                                                          │    │
│  │  Layer 2: DOM autopilot IIFE                             │    │
│  │           ⏱ 1.5s poll · 🛡 2.5s cooldown                │    │
│  │           Continue / Run / Rate Limit → auto-handled     │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  jetskiAgent/main.js  (patched)                          │    │
│  │                                                          │    │
│  │  Layer 1: case "retryable" → auto-retry at source        │    │
│  │           case "generic"   → auto-retry at source        │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  No CDP · No extension · No port conflicts                       │
│  Works across all instances, accounts, and environments          │
└──────────────────────────────────────────────────────────────────┘
```

<br />

---

<br />

## Installation

One step. Under 30 seconds.

No extension. No CDP. No `--remote-debugging-port`. Just run the script.

<details>
<summary><strong>Linux</strong></summary>
<br />

Close all Antigravity instances, then:

```bash
sudo python3 ./patch_antigravity.py
```

Or use the launcher:

```bash
sudo ./patch_antigravity.sh
```

Restart Antigravity. Done.

</details>

<details>
<summary><strong>macOS</strong></summary>
<br />

Close Antigravity, then:

```bash
python3 ./patch_antigravity.py
```

Restart Antigravity.

</details>

<details>
<summary><strong>Windows</strong></summary>
<br />

Close Antigravity, then run:

```
patch_antigravity.cmd
```

Or from PowerShell:

```powershell
python .\patch_antigravity.py
```

Restart Antigravity.

</details>

<br />

**Multiple installations?** Patch them all at once:

```bash
sudo python3 ./patch_antigravity.py --all
```

**That's it.** Every instance, every account, every environment — patched.

<br />

---

<br />

## Configuration

Every feature is toggleable via CLI flags. Mix and match.

<br />

### Defaults

| Feature | Default | Flag to change |
|---------|---------|---------------|
| Auto-Retry | **ON** | `--no-retry` |
| Auto-Continue | **ON** | `--no-continue` |
| Auto-Run | **OFF** | `--enable-run` |
| Rate Limit Handler | **ON** | `--no-ratelimit` |

<br />

### Examples

```bash
# Default: retry + continue + ratelimit ON, run OFF
sudo python3 ./patch_antigravity.py

# Enable auto-run (with default blocklist)
sudo python3 ./patch_antigravity.py --enable-run

# Only auto-retry, nothing else
sudo python3 ./patch_antigravity.py --no-continue --no-ratelimit

# Custom run blocklist
sudo python3 ./patch_antigravity.py --enable-run --run-blocklist "rm -rf" "sudo" "drop "

# Target a specific installation
sudo python3 ./patch_antigravity.py --root /opt/antigravity
```

<br />

### CLI Reference

| Command | Description |
|---------|-------------|
| `python3 patch_antigravity.py` | Patch with default features |
| `python3 patch_antigravity.py --all` | Patch all detected installations |
| `python3 patch_antigravity.py --check` | Check patch status without modifying |
| `python3 patch_antigravity.py --print-paths` | Print detected paths and exit |
| `python3 patch_antigravity.py --restore` | Restore original files from backup |
| `python3 patch_antigravity.py --root <path>` | Specify install root manually |

<br />

---

<br />

## After Antigravity Updates

Antigravity updated and the patch got overwritten? Re-run:

```bash
sudo python3 ./patch_antigravity.py
```

The script automatically:
- Detects the new unpatched version
- Refreshes the backup to match
- Re-applies all patches with your feature configuration

**One command. Always current.**

<br />

---

<br />

## Path Detection

The script automatically locates Antigravity installations:

| Platform | Locations checked |
|----------|------------------|
| **Linux** | `/usr/share/antigravity`, `/usr/lib/antigravity`, `/opt/antigravity`, `~/.local/share/antigravity`, snap, flatpak, glob discovery |
| **macOS** | `/Applications/Antigravity.app` |
| **Windows** | Registry, `%LOCALAPPDATA%\Programs\Antigravity`, common paths, glob discovery |

<br />

If auto-detection fails:

```bash
# Point to the install root
sudo python3 ./patch_antigravity.py --root /path/to/antigravity

# Or set environment variables
export ANTIGRAVITY_INSTALL_DIR=/path/to/antigravity

# Or point directly to the two target files
export ANTIGRAVITY_WORKBENCH_PATH=/path/to/workbench.desktop.main.js
export ANTIGRAVITY_JETSKI_PATH=/path/to/jetskiAgent/main.js
```

<br />

---

<br />

## Security & Safety

| Layer | Protection |
|-------|-----------|
| **Auto-Run off by default** | Must be explicitly enabled with `--enable-run` |
| **Command inspection** | Every command text is read before approval |
| **Configurable blocklist** | 16 dangerous patterns blocked out of the box |
| **Console logging** | All actions and blocked commands logged to DevTools console |
| **No network calls** | Everything runs locally. Zero outbound connections |
| **No telemetry** | Zero data collection. Zero analytics. Zero tracking |
| **Backup & restore** | Original files backed up automatically. `--restore` reverts everything |
| **Open source** | Full source audit available in this repository |

The script **never reads, stores, or transmits your source code**.

<br />

---

<br />

## Monitoring

All autopilot actions are logged to the DevTools console. Open `Ctrl+Shift+I` → Console → filter `[Autopilot]`:

```
[Autopilot] Active | continue=true run=false rateLimit=true
[Autopilot] continues (#1)
[Autopilot] Rate limit detected. Waiting 30s...
[Autopilot] Rate limit wait complete. Resuming.
[Autopilot] retries (#1)
[Autopilot] BLOCKED unsafe command: rm -rf /tmp/important
```

<br />

---

<br />

## Troubleshooting

<details>
<summary><strong>"Could not locate any Antigravity installation"</strong></summary>
<br />

The script couldn't find Antigravity at any default path. Use `--root`:

```bash
sudo python3 ./patch_antigravity.py --root /path/to/antigravity
```

Or check what the script is looking for:

```bash
python3 ./patch_antigravity.py --print-paths
```

</details>

<details>
<summary><strong>"signature not found" on --check</strong></summary>
<br />

The current Antigravity version changed the error notification structure enough that the regex can't match. This happens when Antigravity does a major refactor of the error handling flow (not just variable renames). The patch script needs to be updated to match the new structure.

</details>

<details>
<summary><strong>Permission denied</strong></summary>
<br />

On Linux, system-wide installs (`/usr/share/`) require root:

```bash
sudo python3 ./patch_antigravity.py
```

</details>

<details>
<summary><strong>Want to undo everything</strong></summary>
<br />

```bash
sudo python3 ./patch_antigravity.py --restore
```

This restores the original files from the automatic backups.

</details>

<br />

---

<br />

## FAQ

<details>
<summary><strong>Why not a VS Code extension?</strong></summary>
<br />

The previous version (v2.x) was a VS Code extension using Chrome DevTools Protocol. It required launching Antigravity with `--remote-debugging-port`, created port conflicts with multiple instances, and didn't work in separate environments. Direct file patching solves all of these problems.

</details>

<details>
<summary><strong>Does it work with multiple Antigravity instances?</strong></summary>
<br />

Yes. Since the patch modifies the bundled files on disk, **every instance** that uses those files gets the autopilot behavior. Use `--all` to patch multiple installations at once.

</details>

<details>
<summary><strong>Does it survive Antigravity updates?</strong></summary>
<br />

Updates overwrite the patched files. Re-run the script after each update — it auto-detects the new version, refreshes backups, and re-applies patches. Takes under a second.

</details>

<details>
<summary><strong>Is Auto-Run really safe?</strong></summary>
<br />

Auto-Run is **disabled by default**. When enabled with `--enable-run`, every command is checked against a blocklist before clicking "Run". Operations like `rm -rf`, `sudo`, `shutdown`, `dd`, and `chmod 777` are blocked. You can customize the blocklist with `--run-blocklist`. Blocked commands are logged to the console.

</details>

<details>
<summary><strong>What languages does button detection support?</strong></summary>
<br />

English and Italian. Detected buttons: Retry, Try Again, Riprova, Continue, Continua, Proceed, Yes, Run, Execute, Esegui, Keep Going, Continue Generating.

</details>

<details>
<summary><strong>Can I use only one feature and disable the rest?</strong></summary>
<br />

Yes. Combine flags: `--no-retry --no-continue --no-ratelimit` disables everything except what you leave on. `--enable-run` adds auto-run. Mix and match.

</details>

<br />

---

<br />

## Contributing

Pull requests welcome. If you use a different AI coding editor and want to add support, even better.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a PR

<br />

---

<br />

## License

MIT. See [`LICENSE.txt`](LICENSE.txt).

<br />

## Author

**Guglielmo** — [@guglielmo-io](https://github.com/guglielmo-io)

<br />

---

<div align="center">

<br />

**Stop clicking. Start shipping.**

**[Download Antigravity Autopilot](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)**

<br />

<sub>If this saved you time, give it a star — it helps others find it.</sub>

</div>
