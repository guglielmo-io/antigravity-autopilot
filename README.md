<div align="center">

<img src="https://img.shields.io/badge/Antigravity-Autopilot-blueviolet?style=for-the-badge&logo=visual-studio-code&logoColor=white" alt="Antigravity Autopilot" />

# 🚀 Antigravity Autopilot

### Your AI agent writes the code. Autopilot handles everything else.

**One extension. Zero babysitting. Full autonomy for your AI coding agent.**

<br />

[![GitHub Release](https://img.shields.io/github/v/release/guglielmo-io/antigravity-autopilot?style=flat-square&color=success&label=latest)](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE.txt)
[![Stars](https://img.shields.io/github/stars/guglielmo-io/antigravity-autopilot?style=flat-square&color=yellow)](https://github.com/guglielmo-io/antigravity-autopilot/stargazers)
[![Downloads](https://img.shields.io/github/downloads/guglielmo-io/antigravity-autopilot/total?style=flat-square&color=brightgreen)](https://github.com/guglielmo-io/antigravity-autopilot/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/guglielmo-io/antigravity-autopilot/pulls)

<br />

**Auto-Retry** · **Auto-Continue** · **Auto-Run** · **Rate Limit Handler** · **Session Stats**

<br />

[**⬇️ Download Latest**](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;[Report Bug](https://github.com/guglielmo-io/antigravity-autopilot/issues)&nbsp;&nbsp;&nbsp;·&nbsp;&nbsp;&nbsp;[Request Feature](https://github.com/guglielmo-io/antigravity-autopilot/issues)

</div>

<br />

---

<br />

## Without Autopilot vs With Autopilot

<table>
<tr>
<td width="50%">

### ❌ Before

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

### ✅ After

```
Agent fails → Autopilot clicks Retry
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

## 🧰 Five Features. One Extension. Zero Clicks.

<br />

### 🔄 Auto-Retry — Errors handled instantly

Agent crashed mid-generation? The retry button gets clicked in under 1.5 seconds. Supports **"Retry"**, **"Try Again"**, **"Riprova"**, and more. Multi-language. Multi-window. Always on.

<br />

### ▶️ Auto-Continue — No more "Do you want me to continue?"

Long generation stopped halfway? **"Continue"**, **"Proceed"**, **"Yes"**, **"Continua"** — clicked without you lifting a finger. Chain entire multi-file refactors without touching the keyboard.

<br />

### ⚡ Auto-Run — Safe commands approved automatically

> **Opt-in and guarded by default.** Disabled until you turn it on.

Agent wants to run `npm install` or `mkdir src`? Approved instantly. Tries `rm -rf /` or `sudo`? **Blocked.** Every command is inspected against a configurable blocklist before approval.

**Default blocklist protects against:**

```
rm -rf · rm -r · sudo · drop · delete · format · mkfs
shutdown · reboot · kill -9 · truncate · dd if= · chmod 777 · chown
```

You control the blocklist. Add patterns, remove patterns, make it yours.

<br />

### 🚦 Rate Limit Handler — Wait it out, hands-free

Hit a provider rate limit? Autopilot detects it, reads the wait time, counts down silently, and retries the moment the window opens. Works with messages like **"rate limited"**, **"too many requests"**, **"try again in 30s"**, **"quota exceeded"**.

No staring at a timer. No setting reminders. Just results.

<br />

### 📊 Session Stats — Know what Autopilot did for you

Hover the status bar to see live counts: retries, continues, command approvals, rate limit waits. Run `Autopilot: Show Stats` in the Command Palette for a full session summary.

Real numbers. Proof it's working.

<br />

---

<br />

## 📦 Installation

Two steps. Under 2 minutes.

### Step 1: Enable Chrome DevTools Protocol (one-time)

Antigravity needs to expose a debugging port so Autopilot can inject its automation.

<details>
<summary><strong>🐧 Linux</strong></summary>
<br />

Edit `~/.local/share/applications/antigravity.desktop`:

```ini
Exec=/usr/share/antigravity/antigravity --remote-debugging-port=9222 %F
```

</details>

<details>
<summary><strong>🍎 macOS</strong></summary>
<br />

Add to your shell config (`~/.zshrc` or `~/.bashrc`):

```bash
alias antigravity='/Applications/Antigravity.app/Contents/MacOS/Antigravity --remote-debugging-port=9222'
```

Launch from terminal: `antigravity`

</details>

<details>
<summary><strong>🪟 Windows</strong></summary>
<br />

Right-click your Antigravity shortcut → **Properties** → **Target**:

```
"C:\Users\YOUR_USERNAME\AppData\Local\Programs\Antigravity\Antigravity.exe" --remote-debugging-port=9222
```

</details>

<br />

### Step 2: Install the extension

**Option A: GUI (Recommended)**

1. Download [`antigravity-autopilot-2.0.0.vsix`](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)
2. Open Antigravity → `Ctrl+Shift+P` → `Extensions: Install from VSIX...`
3. Select the file. Done.

**Option B: Terminal**

```bash
# Linux
antigravity --install-extension antigravity-autopilot-2.0.0.vsix

# macOS
/Applications/Antigravity.app/Contents/MacOS/Antigravity --install-extension antigravity-autopilot-2.0.0.vsix

# Windows (PowerShell)
& "$env:LOCALAPPDATA\Programs\Antigravity\Antigravity.exe" --install-extension antigravity-autopilot-2.0.0.vsix
```

**That's it.** Autopilot starts automatically on next launch.

<br />

---

<br />

## 🎮 Usage

### Status Bar

| Indicator | State |
|-----------|-------|
| `🚀 Autopilot: ON` | Active — all enabled features are running |
| `⭕ Autopilot: OFF` | Disabled |

Hover for live session stats and active feature list.

### Command Palette (`Ctrl+Shift+P`)

| Command | What it does |
|---------|-------------|
| `Autopilot: Start` | Activate all enabled features |
| `Autopilot: Stop` | Stop automation and clean up connections |
| `Autopilot: Show Stats` | Full session report: features, windows, action counts |

<br />

---

<br />

## ⚙️ Configuration

Open **Settings** → search `autopilot`. Every feature toggles independently.

| Setting | Type | Default | What it controls |
|---------|------|---------|-----------------|
| `autopilot.enabled` | boolean | `true` | Start on launch |
| `autopilot.cdpPort` | number | `0` | CDP port (`0` = auto-scan 9222, 9000-9003) |
| `autopilot.autoRetry` | boolean | `true` | Click retry on agent errors |
| `autopilot.autoContinue` | boolean | `true` | Click continue on generation pauses |
| `autopilot.autoRun` | boolean | **`false`** | Approve safe commands *(opt-in)* |
| `autopilot.runBlocklist` | string[] | *[see above](#-auto-run--safe-commands-approved-automatically)* | Patterns to never auto-approve |
| `autopilot.rateLimitHandler` | boolean | `true` | Auto-wait and retry on rate limits |
| `autopilot.showStats` | boolean | `true` | Live stats in status bar tooltip |

> **Only want Auto-Retry?** Turn off the rest. Only want Auto-Continue? Same. Mix and match.

<br />

---

<br />

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      Antigravity Window                          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                 Agent Panel (sandboxed iframe)              │  │
│  │                                                             │  │
│  │    ❌ Error        →  [ Retry ]    ←  auto-clicked          │  │
│  │    ⏸️ Paused       →  [ Continue ] ←  auto-clicked          │  │
│  │    💻 npm install  →  [ Run ]      ←  auto-approved (safe)  │  │
│  │    🚦 Rate limited →  waiting...   ←  auto-retried          │  │
│  │                                                             │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              ▲                                    │
│                    CDP WebSocket connection                       │
│                              ▲                                    │
│                 ┌────────────┴────────────┐                      │
│                 │    Autopilot Engine     │                      │
│                 │                         │                      │
│                 │  ⏱ 1.5s scan interval  │                      │
│                 │  🛡 2.5s click cooldown │                      │
│                 │  🪟 Multi-window aware  │                      │
│                 │  🔒 Command blocklist   │                      │
│                 │  📊 Live stat tracking  │                      │
│                 └─────────────────────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

**How it works under the hood:**

1. Connects to Antigravity via **Chrome DevTools Protocol** (WebSocket on port 9222)
2. Discovers all open windows. Injects a lightweight automation script into each one.
3. The script scans the agent panel iframe every **1.5 seconds** for actionable buttons.
4. When a match is found, it clicks — with a **2.5-second cooldown** to prevent double-clicks.
5. Auto-Run inspects command text in nearby code blocks before approving, checking every entry in the blocklist.
6. Rate Limit Handler parses wait durations directly from the error message, then auto-retries after the countdown.
7. Session stats are polled back to the extension every 5 seconds for live tooltip updates.

**Under 10KB.** Zero external API calls. Zero telemetry. Your code, your machine, your data.

<br />

---

<br />

## 🔒 Security & Safety

| Layer | Protection |
|-------|-----------|
| **Auto-Run off by default** | Must be explicitly enabled in settings |
| **Command inspection** | Every command text is read before approve |
| **Configurable blocklist** | 16 dangerous patterns blocked out of the box |
| **Console logging** | Blocked commands logged for full transparency |
| **No network calls** | Extension communicates only with localhost CDP |
| **No telemetry** | Zero data collection. Zero analytics. Zero tracking |
| **Open source** | Full source audit available in this repository |

The extension **never reads, stores, or transmits your source code**.

<br />

---

<br />

## 🔧 Troubleshooting

<details>
<summary><strong>"CDP not available" error</strong></summary>
<br />

Antigravity was not launched with the `--remote-debugging-port` flag. See [Installation Step 1](#step-1-enable-chrome-devtools-protocol-one-time).

Verify CDP is active:

```bash
curl http://127.0.0.1:9222/json/version
```

A JSON response means it's working.

</details>

<details>
<summary><strong>Using a non-standard CDP port</strong></summary>
<br />

Set `autopilot.cdpPort` to your port number in Settings. When set to `0` (default), Autopilot auto-scans ports `9222, 9000, 9001, 9002, 9003`.

</details>

<details>
<summary><strong>Extension not activating after install</strong></summary>
<br />

1. Reload: `Ctrl+Shift+P` → `Developer: Reload Window`
2. Check output: `Ctrl+Shift+U` → select **"Antigravity Autopilot"**

</details>

<br />

---

<br />

## ❓ FAQ

<details>
<summary><strong>Does this work with VS Code, Cursor, or Windsurf?</strong></summary>
<br />

Autopilot is built for **Antigravity** (a VS Code fork with a built-in AI agent). It may work with other Electron-based editors that expose CDP, but compatibility is not guaranteed. Contributions to support other editors are welcome.

</details>

<details>
<summary><strong>Does it work over Remote SSH?</strong></summary>
<br />

Yes. The extension declares `extensionKind: ["ui"]`, so it always runs on your **local machine** where CDP is accessible. No manual configuration needed.

</details>

<details>
<summary><strong>Is Auto-Run really safe?</strong></summary>
<br />

Auto-Run is **disabled by default**. When you opt in, every command is checked against a blocklist before clicking "Run". Operations like `rm -rf`, `sudo`, `shutdown`, `dd`, and `chmod 777` are blocked. You can extend the blocklist with your own patterns. Blocked commands are logged to the developer console.

</details>

<details>
<summary><strong>Can I use only one feature and disable the rest?</strong></summary>
<br />

Yes. Every feature has its own toggle in Settings. Turn on what you need, turn off what you don't.

</details>

<details>
<summary><strong>What languages does button detection support?</strong></summary>
<br />

English and Italian. Detected buttons include: Retry, Try Again, Riprova, Continue, Continua, Proceed, Yes, Run, Execute, Esegui, Keep Going, Continue Generating.

</details>

<details>
<summary><strong>Does it use my API key or send data anywhere?</strong></summary>
<br />

No. Autopilot runs entirely on your local machine. It communicates only with `127.0.0.1` via CDP. Zero network requests. Zero telemetry.

</details>

<details>
<summary><strong>How much CPU does it use?</strong></summary>
<br />

The injected script runs a lightweight DOM scan every 1.5 seconds. The extension itself polls stats every 5 seconds. Total overhead is negligible — well under 0.1% CPU on modern hardware.

</details>

<br />

---

<br />

## 🌟 Star History

If Autopilot saved you from clicking through another wall of retry prompts, a ⭐ helps others find it.

<a href="https://star-history.com/#guglielmo-io/antigravity-autopilot&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=guglielmo-io/antigravity-autopilot&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=guglielmo-io/antigravity-autopilot&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=guglielmo-io/antigravity-autopilot&type=Date" />
 </picture>
</a>

<br />

---

<br />

## 🤝 Contributing

Pull requests welcome. If you use a different AI coding editor and want to add support, even better.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a PR

<br />

---

<br />

## 📄 License

MIT. See [`LICENSE.txt`](extension/LICENSE.txt).

<br />

## 👤 Author

**Guglielmo** — [@guglielmo-io](https://github.com/guglielmo-io)

<br />

---

<div align="center">

<br />

**Stop clicking. Start shipping.**

**[⬇️ Download Antigravity Autopilot](https://github.com/guglielmo-io/antigravity-autopilot/releases/latest)**

<br />

<sub>If this extension saved you time, give it a ⭐ — it helps others find it.</sub>

</div>
