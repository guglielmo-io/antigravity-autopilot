#!/usr/bin/env python3
"""
Antigravity Autopilot Patch

Full autopilot for Antigravity — patches bundled JS files directly.
No extension, no CDP, no --remote-debugging-port.

Features:
  - Auto-Retry: intercepts retryable/generic error branches at source level
  - Auto-Continue: DOM-polls for continue/proceed buttons and clicks them
  - Auto-Run: opt-in safe command approval with configurable blocklist
  - Rate Limit Handler: detects rate-limit messages, waits, then retries
  - Stats: logs action counts to devtools console

Structure-based patching — survives minified variable renames across updates.
Supports Linux, macOS, and Windows with automatic install detection.
"""

import argparse
import glob
import json
import os
import platform
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKBENCH_REL = Path("resources") / "app" / "out" / "vs" / "workbench" / "workbench.desktop.main.js"
JETSKI_REL = Path("resources") / "app" / "out" / "jetskiAgent" / "main.js"

ENV_INSTALL_DIR = "ANTIGRAVITY_INSTALL_DIR"
ENV_WORKBENCH_PATH = "ANTIGRAVITY_WORKBENCH_PATH"
ENV_JETSKI_PATH = "ANTIGRAVITY_JETSKI_PATH"

MAC_APP_BUNDLE = Path("/Applications/Antigravity.app")
MAC_CONTENTS_ROOT = MAC_APP_BUNDLE / "Contents"

AUTO_RETRY_SET = "__agAutoRetryIds"
AUTO_RETRY_NOTIF = "__agAutoRetryNotification"

AUTOPILOT_SENTINEL_START = "/* __ANTIGRAVITY_AUTOPILOT_START__ */"
AUTOPILOT_SENTINEL_END = "/* __ANTIGRAVITY_AUTOPILOT_END__ */"


# ---------------------------------------------------------------------------
# Autopilot config
# ---------------------------------------------------------------------------

DEFAULT_RUN_BLOCKLIST = [
    "rm -rf", "rm -r", "sudo", "drop ", "delete ", "format ",
    "mkfs", "shutdown", "reboot", "kill -9", "truncate",
    ":>", "> /dev", "dd if=", "chmod 777", "chown",
]


@dataclass
class AutopilotConfig:
    auto_retry: bool = True
    auto_continue: bool = True
    auto_run: bool = False
    run_blocklist: list = field(default_factory=lambda: list(DEFAULT_RUN_BLOCKLIST))
    rate_limit_handler: bool = True
    check_interval_ms: int = 1500
    click_cooldown_ms: int = 2500


# ---------------------------------------------------------------------------
# Case-level auto-retry patches (switch branch interception)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CasePatch:
    case_name: str
    primary_label: str
    primary_message: str
    pattern: "re.Pattern[str]"


def _build_pattern(case_name: str, primary_label: str, primary_message: str) -> "re.Pattern[str]":
    return re.compile(
        rf'case"{re.escape(case_name)}":return(?P<object>\{{id:(?P<id>[^,]+),(?P<middle>.*?)'
        rf'primaryAction:(?P<primary>[A-Za-z_$][\w$]*)\("{re.escape(primary_label)}","{re.escape(primary_message)}"\),'
        rf'secondaryAction:(?P<secondary>[A-Za-z_$][\w$]*)\(\)\}})',
        re.DOTALL,
    )


CASE_PATCHES = [
    CasePatch("retryable", "Try again", "Try again",
              _build_pattern("retryable", "Try again", "Try again")),
    CasePatch("generic", "Retry", "Continue",
              _build_pattern("generic", "Retry", "Continue")),
]


# ---------------------------------------------------------------------------
# DOM-polling autopilot script (injected into workbench JS)
# ---------------------------------------------------------------------------

def build_autopilot_script(config: AutopilotConfig) -> str:
    """Build the self-contained autopilot IIFE to inject into the workbench."""
    cfg_json = json.dumps({
        "autoContinue": config.auto_continue,
        "autoRun": config.auto_run,
        "runBlocklist": config.run_blocklist,
        "rateLimitHandler": config.rate_limit_handler,
        "checkInterval": config.check_interval_ms,
        "clickCooldown": config.click_cooldown_ms,
    })

    return f"""\n{AUTOPILOT_SENTINEL_START}
;(function(){{
if(globalThis.__autopilotInjected)return;
globalThis.__autopilotInjected=true;

var CFG={cfg_json};

var stats={{retries:0,continues:0,runs:0,rateLimitWaits:0}};
var lastClick=0;
var rateLimitActive=false;

var RETRY_TEXTS=['retry','try again','riprova','riprovare'];
var CONTINUE_TEXTS=['continue','continua','proceed','yes','continue generating','keep going'];
var RUN_TEXTS=['run','run command','execute','run in terminal','esegui'];
var RATE_LIMIT_PATTERNS=[
  'rate limit','too many requests','try again in','try again later',
  'limite di frequenza','limit reached','quota exceeded','throttled',
  'please wait','slow down'
];

function isVisible(el){{
  if(!el)return false;
  var s=window.getComputedStyle(el);
  return s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0'&&el.offsetParent!==null;
}}

function isClickable(el){{
  return el&&!el.disabled&&el.getAttribute('aria-disabled')!=='true'&&isVisible(el);
}}

function findButton(doc,textList){{
  if(!doc)return null;
  var sels=['button','[role="button"]','a','.monaco-button','.action-label'];
  for(var si=0;si<sels.length;si++){{
    try{{
      var els=doc.querySelectorAll(sels[si]);
      for(var ei=0;ei<els.length;ei++){{
        var t=(els[ei].textContent||'').trim().toLowerCase();
        for(var ti=0;ti<textList.length;ti++){{
          if(t===textList[ti]||t.indexOf(textList[ti])===0){{
            if(isClickable(els[ei]))return els[ei];
          }}
        }}
      }}
    }}catch(e){{}}
  }}
  return null;
}}

function getCommandText(btn){{
  try{{
    var node=btn.parentElement;
    for(var i=0;i<5&&node;i++){{
      var cb=node.querySelector('pre,code,.monaco-editor,[class*="code-block"]');
      if(cb)return(cb.textContent||'').trim().toLowerCase();
      node=node.parentElement;
    }}
    var prev=btn.previousElementSibling;
    if(prev){{
      var c=prev.querySelector('pre,code');
      if(c)return(c.textContent||'').trim().toLowerCase();
    }}
  }}catch(e){{}}
  return '';
}}

function isCommandSafe(cmd){{
  if(!cmd)return true;
  var lower=cmd.toLowerCase();
  for(var i=0;i<CFG.runBlocklist.length;i++){{
    if(lower.indexOf(CFG.runBlocklist[i].toLowerCase())!==-1)return false;
  }}
  return true;
}}

function detectRateLimit(doc){{
  if(!doc)return null;
  try{{
    var body=(doc.body&&doc.body.textContent||'').toLowerCase();
    for(var i=0;i<RATE_LIMIT_PATTERNS.length;i++){{
      if(body.indexOf(RATE_LIMIT_PATTERNS[i])!==-1){{
        var m=body.match(/(?:try again in|wait|attendi)\\s*(\\d+)\\s*(?:second|sec|s)/i);
        return{{detected:true,waitSeconds:m?parseInt(m[1],10):15}};
      }}
    }}
  }}catch(e){{}}
  return null;
}}

function clickWithCooldown(el,actionType){{
  var now=Date.now();
  if(now-lastClick<CFG.clickCooldown)return false;
  lastClick=now;
  stats[actionType]++;
  el.click();
  console.log('[Autopilot] '+actionType+' (#'+stats[actionType]+')');
  globalThis.__autopilotStats=JSON.parse(JSON.stringify(stats));
  return true;
}}

function getAgentDoc(){{
  try{{
    var frame=document.getElementById('antigravity.agentPanel');
    if(frame&&frame.contentDocument&&frame.contentDocument.readyState==='complete')return frame.contentDocument;
  }}catch(e){{}}
  var container=document.getElementById('antigravity.agentViewContainerId');
  if(container)return document;
  return document;
}}

function check(){{
  try{{
    var doc=getAgentDoc();
    if(!doc)return;
    if(rateLimitActive)return;

    if(CFG.rateLimitHandler){{
      var rl=detectRateLimit(doc);
      if(rl&&rl.detected){{
        rateLimitActive=true;
        stats.rateLimitWaits++;
        globalThis.__autopilotStats=JSON.parse(JSON.stringify(stats));
        var waitMs=rl.waitSeconds*1000+2000;
        console.log('[Autopilot] Rate limit detected. Waiting '+rl.waitSeconds+'s...');
        setTimeout(function(){{
          rateLimitActive=false;
          console.log('[Autopilot] Rate limit wait complete. Resuming.');
          var rb=findButton(doc,RETRY_TEXTS);
          if(rb)clickWithCooldown(rb,'retries');
        }},waitMs);
        return;
      }}
    }}

    var retryBtn=findButton(doc,RETRY_TEXTS);
    if(retryBtn){{
      clickWithCooldown(retryBtn,'retries');
      return;
    }}

    if(CFG.autoContinue){{
      var contBtn=findButton(doc,CONTINUE_TEXTS);
      if(contBtn){{
        clickWithCooldown(contBtn,'continues');
        return;
      }}
    }}

    if(CFG.autoRun){{
      var runBtn=findButton(doc,RUN_TEXTS);
      if(runBtn){{
        var cmd=getCommandText(runBtn);
        if(isCommandSafe(cmd)){{
          clickWithCooldown(runBtn,'runs');
        }}else{{
          console.log('[Autopilot] BLOCKED unsafe command: '+cmd.substring(0,80));
        }}
        return;
      }}
    }}
  }}catch(e){{}}
}}

function start(){{
  globalThis.__autopilotInterval=setInterval(check,CFG.checkInterval);
  globalThis.__autopilotStats=stats;
  console.log('[Autopilot] Active | continue='+CFG.autoContinue+' run='+CFG.autoRun+' rateLimit='+CFG.rateLimitHandler);
}}

if(document.readyState==='complete'||document.readyState==='interactive'){{
  setTimeout(start,3000);
}}else{{
  document.addEventListener('DOMContentLoaded',function(){{setTimeout(start,3000);}});
}}
}})();
{AUTOPILOT_SENTINEL_END}"""


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def backup_path_for(path: Path) -> Path:
    return Path(f"{path}.bak")


def dedupe_paths(paths: List[Path]) -> List[Path]:
    result: List[Path] = []
    seen: Set[str] = set()
    for p in paths:
        try:
            norm = str(p.expanduser().resolve(strict=False))
        except OSError:
            norm = str(p.expanduser())
        if norm not in seen:
            seen.add(norm)
            result.append(Path(norm))
    return result


def strip_autopilot_injection(content: str) -> str:
    """Remove any existing autopilot IIFE injection from file content."""
    start = content.find(AUTOPILOT_SENTINEL_START)
    end = content.find(AUTOPILOT_SENTINEL_END)
    if start != -1 and end != -1:
        return content[:start].rstrip() + content[end + len(AUTOPILOT_SENTINEL_END):]
    return content


def has_autopilot_injection(content: str) -> bool:
    return AUTOPILOT_SENTINEL_START in content and AUTOPILOT_SENTINEL_END in content


# ---------------------------------------------------------------------------
# Install discovery
# ---------------------------------------------------------------------------

def pair_from_base(base: Path) -> Optional[Tuple[Path, Path]]:
    wb = base / WORKBENCH_REL
    js = base / JETSKI_REL
    if wb.is_file() and js.is_file():
        return wb, js
    return None


def resolve_pair(hint: Path) -> Optional[Tuple[Path, Path]]:
    hint = hint.expanduser()
    candidates: List[Path] = []
    if hint.is_file():
        candidates.extend(list(hint.parents))
    else:
        candidates.append(hint)
        candidates.append(hint / "Contents")
        candidates.extend(list(hint.parents))
    for c in dedupe_paths(candidates):
        pair = pair_from_base(c)
        if pair:
            return pair
    return None


def _extract_fs_path(raw: str) -> Optional[Path]:
    text = raw.strip().strip('"')
    if not text:
        return None
    if text.lower().endswith(".exe,0"):
        text = text[:-2]
    elif ".exe," in text.lower():
        text = text.rsplit(",", 1)[0]
    p = Path(text)
    return p if p.exists() else None


def _linux_roots() -> List[Path]:
    home = Path.home()
    return dedupe_paths([
        Path("/usr/share/antigravity"),
        Path("/usr/lib/antigravity"),
        Path("/opt/antigravity"),
        home / ".local" / "share" / "antigravity",
        home / ".local" / "share" / "Antigravity",
        Path("/snap/antigravity/current"),
        Path("/var/lib/flatpak/app/com.antigravity.Antigravity/current/active/files"),
        home / ".local" / "share" / "flatpak" / "app" / "com.antigravity.Antigravity" / "current" / "active" / "files",
    ])


def _linux_glob_roots() -> List[Path]:
    candidates: List[Path] = []
    search_dirs = [
        Path("/usr/share"), Path("/usr/lib"), Path("/opt"),
        Path.home() / ".local" / "share",
        Path.home() / ".local" / "lib",
    ]
    patterns = ["*ntigravity*", "*antigravity*", "*cloud-code*", "*Cloud?Code*"]
    for base in search_dirs:
        if not base.exists():
            continue
        for pat in patterns:
            for match in glob.glob(str(base / pat)):
                candidates.append(Path(match))
    return dedupe_paths(candidates)


def _windows_registry_roots() -> List[Path]:
    roots: List[Path] = []
    try:
        import winreg
    except ImportError:
        return roots
    uninstall_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    hints = ("antigravity", "cloud code")
    for hive, subkey in uninstall_keys:
        try:
            parent_key = winreg.OpenKey(hive, subkey)
        except OSError:
            continue
        try:
            child_count = winreg.QueryInfoKey(parent_key)[0]
            for idx in range(child_count):
                try:
                    child_name = winreg.EnumKey(parent_key, idx)
                    app_key = winreg.OpenKey(parent_key, child_name)
                except OSError:
                    continue
                with app_key:
                    combined = ""
                    for name in ("DisplayName", "InstallLocation", "DisplayIcon"):
                        try:
                            val, _ = winreg.QueryValueEx(app_key, name)
                            combined += f" {val}" if isinstance(val, str) else ""
                        except OSError:
                            pass
                    if not any(h in combined.lower() for h in hints):
                        continue
                    for name in ("InstallLocation", "DisplayIcon"):
                        try:
                            val, _ = winreg.QueryValueEx(app_key, name)
                        except OSError:
                            continue
                        extracted = _extract_fs_path(val)
                        if extracted:
                            roots.append(extracted if extracted.is_dir() else extracted.parent)
        finally:
            winreg.CloseKey(parent_key)
    return dedupe_paths(roots)


def _windows_default_roots() -> List[Path]:
    home = Path.home()
    la = home / "AppData" / "Local"
    return dedupe_paths([
        la / "Programs" / "Antigravity",
        la / "Programs" / "antigravity-stable-user-x64",
        la / "Programs" / "Cloud Code",
        la / "Antigravity",
        Path(r"C:\Antigravity"),
        Path(r"D:\Antigravity"),
    ])


def _windows_glob_roots() -> List[Path]:
    candidates: List[Path] = []
    la = Path(os.environ.get("LOCALAPPDATA", "")) or Path.home() / "AppData" / "Local"
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
    pf86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
    patterns = ["*Antigravity*", "*antigravity*", "*Cloud Code*", "*cloud code*", "*cloud-code*"]
    for base in (la / "Programs", la, pf, pf86):
        if not base.exists():
            continue
        for pat in patterns:
            for match in glob.glob(str(base / pat)):
                root = Path(match)
                candidates.append(root)
                for child in ("app-*", "current"):
                    candidates.extend(root.glob(child))
    return dedupe_paths(candidates)


def discover_all_installs(manual_root: Optional[str] = None) -> List[Tuple[Path, Path, str]]:
    ew = os.environ.get(ENV_WORKBENCH_PATH)
    ej = os.environ.get(ENV_JETSKI_PATH)
    if ew or ej:
        if not (ew and ej):
            print(f"[ERROR] {ENV_WORKBENCH_PATH} and {ENV_JETSKI_PATH} must be set together.", file=sys.stderr)
            return []
        wb, js = Path(ew).expanduser(), Path(ej).expanduser()
        if wb.is_file() and js.is_file():
            return [(wb, js, "environment file override")]
        print("[ERROR] Environment override paths do not point to existing files.", file=sys.stderr)
        return []

    hints: List[Tuple[str, Path]] = []
    if manual_root:
        hints.append(("--root", Path(manual_root).expanduser()))
    env_root = os.environ.get(ENV_INSTALL_DIR)
    if env_root:
        hints.append((ENV_INSTALL_DIR, Path(env_root).expanduser()))

    system = platform.system()
    if system == "Linux":
        hints.extend(("linux-default", p) for p in _linux_roots())
        hints.extend(("linux-glob", p) for p in _linux_glob_roots())
    if system == "Windows":
        hints.extend(("registry", p) for p in _windows_registry_roots())
        hints.extend(("default", p) for p in _windows_default_roots())
        hints.extend(("glob", p) for p in _windows_glob_roots())
    hints.append(("macOS-default", MAC_CONTENTS_ROOT))
    hints.append(("macOS-app-bundle", MAC_APP_BUNDLE))

    results: List[Tuple[Path, Path, str]] = []
    seen_wb: Set[str] = set()
    for source, hint in hints:
        pair = resolve_pair(hint)
        if not pair:
            continue
        wb_norm = str(pair[0].resolve())
        if wb_norm in seen_wb:
            continue
        seen_wb.add(wb_norm)
        results.append((pair[0], pair[1], f"{source}: {hint}"))
    return results


def discover_paths(manual_root: Optional[str] = None) -> Optional[Tuple[Path, Path, str]]:
    installs = discover_all_installs(manual_root)
    return installs[0] if installs else None


# ---------------------------------------------------------------------------
# Case-level patch logic (auto-retry at source)
# ---------------------------------------------------------------------------

def _current_marker(case_name: str) -> str:
    return f'case"{case_name}":{{let {AUTO_RETRY_NOTIF}='


def _legacy_marker(case_name: str) -> str:
    return f'case"{case_name}":{{if(!globalThis._agRetried)'


def _build_replacement(case_name: str, object_expr: str) -> str:
    n = AUTO_RETRY_NOTIF
    s = AUTO_RETRY_SET
    return (
        f'case"{case_name}":{{let {n}={object_expr};'
        f"if(!globalThis.{s})globalThis.{s}=new Set;"
        f"if(!globalThis.{s}.has({n}.id)){{"
        f"globalThis.{s}.add({n}.id);"
        f"return setTimeout(()=>{{{n}.primaryAction.onClick()}},500),void 0}}"
        f"return {n}}}"
    )


def case_status(content: str, patch: CasePatch) -> Tuple[str, str]:
    if _current_marker(patch.case_name) in content:
        return "patched", "already patched (current)"
    if _legacy_marker(patch.case_name) in content:
        return "patched", "already patched (legacy)"
    matches = list(patch.pattern.finditer(content))
    if len(matches) == 1:
        return "patchable", "signature found"
    if len(matches) == 0:
        return "missing", "signature not found"
    return "ambiguous", f"signature matched {len(matches)} times"


def _is_fully_unpatched(content: str) -> bool:
    clean = strip_autopilot_injection(content)
    return all(case_status(clean, p)[0] == "patchable" for p in CASE_PATCHES)


def apply_case_patch(content: str, patch: CasePatch) -> Tuple[str, bool, str]:
    status, detail = case_status(content, patch)
    if status == "patched":
        return content, False, f"{patch.case_name}: {detail}"
    if status in ("missing", "ambiguous"):
        return content, False, f"{patch.case_name}: {detail}"
    match = list(patch.pattern.finditer(content))[0]
    replacement = _build_replacement(patch.case_name, match.group("object"))
    updated, count = patch.pattern.subn(replacement, content, count=1)
    if count != 1:
        return content, False, f"{patch.case_name}: replacement failed"
    return updated, True, f"{patch.case_name}: patch applied"


# ---------------------------------------------------------------------------
# File-level operations
# ---------------------------------------------------------------------------

def _manage_backup(filepath: Path, content: str) -> None:
    backup = backup_path_for(filepath)
    clean_content = strip_autopilot_injection(content)
    if not backup.exists():
        shutil.copy2(filepath, backup)
        print(f"  [OK] Backup created: {backup.name}")
    elif _is_fully_unpatched(content) and not has_autopilot_injection(content) and read_text(backup) != content:
        shutil.copy2(filepath, backup)
        print(f"  [OK] Backup refreshed (new app version): {backup.name}")
    else:
        print(f"  [OK] Existing backup: {backup.name}")


def patch_workbench(filepath: Path, config: AutopilotConfig) -> bool:
    """Apply case patches + autopilot DOM script to workbench file."""
    if not filepath.exists():
        print(f"  [ERROR] File not found: {filepath}")
        return False

    content = read_text(filepath)
    _manage_backup(filepath, content)

    # Strip old autopilot injection before re-patching
    content = strip_autopilot_injection(content)

    updated = content
    changed = False

    # 1) Case-level auto-retry patches
    if config.auto_retry:
        for i, cp in enumerate(CASE_PATCHES, 1):
            updated, case_changed, msg = apply_case_patch(updated, cp)
            if any(w in msg for w in ("not found", "matched", "failed")):
                print(f"  [ERROR] Patch {i} {msg}")
                return False
            changed = changed or case_changed
            print(f"  [OK] Retry patch {i} — {msg}")
    else:
        print("  [--] Auto-retry disabled, skipping case patches")

    # 2) Autopilot DOM-polling script injection
    needs_autopilot = config.auto_continue or config.auto_run or config.rate_limit_handler
    if needs_autopilot:
        autopilot_js = build_autopilot_script(config)
        updated = updated + autopilot_js
        changed = True
        features = []
        if config.auto_continue:
            features.append("continue")
        if config.auto_run:
            features.append("run")
        if config.rate_limit_handler:
            features.append("ratelimit")
        print(f"  [OK] Autopilot script injected ({', '.join(features)})")
    else:
        print("  [--] No DOM autopilot features enabled")

    if changed:
        write_text(filepath, updated)
        print("  [OK] File updated")
    else:
        print("  [OK] No changes needed")
    return True


def patch_jetski(filepath: Path, config: AutopilotConfig) -> bool:
    """Apply case patches only to jetski agent file."""
    if not filepath.exists():
        print(f"  [ERROR] File not found: {filepath}")
        return False

    content = read_text(filepath)
    _manage_backup(filepath, content)

    updated = content
    changed = False

    if config.auto_retry:
        for i, cp in enumerate(CASE_PATCHES, 1):
            updated, case_changed, msg = apply_case_patch(updated, cp)
            if any(w in msg for w in ("not found", "matched", "failed")):
                print(f"  [ERROR] Patch {i} {msg}")
                return False
            changed = changed or case_changed
            print(f"  [OK] Retry patch {i} — {msg}")
    else:
        print("  [--] Auto-retry disabled, skipping case patches")

    if changed:
        write_text(filepath, updated)
        print("  [OK] File updated")
    else:
        print("  [OK] No changes needed")
    return True


def check_file(filepath: Path, is_workbench: bool = False) -> bool:
    if not filepath.exists():
        print(f"  [ERROR] File not found: {filepath}")
        return False
    content = read_text(filepath)
    ok = True
    for cp in CASE_PATCHES:
        status, detail = case_status(content, cp)
        if status in ("patched", "patchable"):
            print(f"  [OK] {cp.case_name}: {detail}")
        else:
            ok = False
            print(f"  [WARN] {cp.case_name}: {detail}")
    if is_workbench:
        if has_autopilot_injection(content):
            print("  [OK] autopilot: DOM script injected")
        else:
            print("  [--] autopilot: DOM script not present")
    return ok


def restore_file(filepath: Path) -> bool:
    backup = backup_path_for(filepath)
    if not backup.exists():
        print(f"  [ERROR] Backup not found: {backup}")
        return False
    shutil.copy2(backup, filepath)
    print(f"  [OK] Restored: {filepath.name}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Antigravity Autopilot — patch bundled JS for auto-retry, auto-continue, auto-run, and rate limit handling."
    )
    p.add_argument("--root", help="Antigravity install root (or .app / exe directory).")
    p.add_argument("--all", action="store_true", help="Patch all detected installations.")
    p.add_argument("--print-paths", action="store_true", help="Print detected file paths and exit.")
    p.add_argument("--restore", action="store_true", help="Restore backed-up original files.")
    p.add_argument("--check", action="store_true", help="Check if files are patchable / already patched.")

    feat = p.add_argument_group("feature toggles")
    feat.add_argument("--no-retry", action="store_true", help="Disable auto-retry (case-level patches).")
    feat.add_argument("--no-continue", action="store_true", help="Disable auto-continue.")
    feat.add_argument("--enable-run", action="store_true", help="Enable auto-run (off by default, blocklist-guarded).")
    feat.add_argument("--no-ratelimit", action="store_true", help="Disable rate limit handler.")
    feat.add_argument("--run-blocklist", nargs="*", help="Override run blocklist patterns.")

    return p.parse_args()


def build_config(args: argparse.Namespace) -> AutopilotConfig:
    config = AutopilotConfig()
    if args.no_retry:
        config.auto_retry = False
    if args.no_continue:
        config.auto_continue = False
    if args.enable_run:
        config.auto_run = True
    if args.no_ratelimit:
        config.rate_limit_handler = False
    if args.run_blocklist is not None:
        config.run_blocklist = args.run_blocklist
    return config


def _print_header(wb: Path, js: Path, source: str, index: int = 0) -> None:
    if index == 0:
        print("=" * 64)
        print("  Antigravity Autopilot Patch")
        print("=" * 64)
    if index > 0:
        print(f"\n--- Installation #{index + 1} ---")
    print(f"  Source     : {source}")
    print(f"  Workbench  : {wb}")
    print(f"  JetskiAgent: {js}")


def _process_install(wb: Path, js: Path, args: argparse.Namespace, config: AutopilotConfig) -> bool:
    if args.restore:
        print("\n  [1/2] Restoring workbench.desktop.main.js")
        r1 = restore_file(wb)
        print("  [2/2] Restoring jetskiAgent/main.js")
        r2 = restore_file(js)
    elif args.check:
        print("\n  [1/2] Checking workbench.desktop.main.js")
        r1 = check_file(wb, is_workbench=True)
        print("  [2/2] Checking jetskiAgent/main.js")
        r2 = check_file(js)
    else:
        features = []
        if config.auto_retry:
            features.append("retry")
        if config.auto_continue:
            features.append("continue")
        if config.auto_run:
            features.append("run")
        if config.rate_limit_handler:
            features.append("ratelimit")
        print(f"\n  Features: {', '.join(features) if features else 'none'}")
        print("\n  [1/2] Patching workbench.desktop.main.js")
        r1 = patch_workbench(wb, config)
        print("  [2/2] Patching jetskiAgent/main.js")
        r2 = patch_jetski(js, config)
    return r1 and r2


def main() -> int:
    args = parse_args()
    config = build_config(args)

    if args.all:
        installs = discover_all_installs(args.root)
    else:
        found = discover_paths(args.root)
        installs = [found] if found else []

    if not installs:
        print("=" * 64)
        print("  Antigravity Autopilot Patch")
        print("=" * 64)
        print("[ERROR] Could not locate any Antigravity installation.")
        print("Try one of:")
        print('  1. --root "/path/to/antigravity"')
        print(f"  2. export {ENV_INSTALL_DIR}=/path/to/antigravity")
        print(f"  3. export {ENV_WORKBENCH_PATH}=... and {ENV_JETSKI_PATH}=...")
        return 1

    for i, (wb, js, source) in enumerate(installs):
        _print_header(wb, js, source, i)

    if args.print_paths:
        return 0

    all_ok = True
    for i, (wb, js, source) in enumerate(installs):
        if len(installs) > 1:
            print(f"\n{'─' * 48}")
            print(f"  Processing #{i + 1}: {source}")
            print(f"{'─' * 48}")
        ok = _process_install(wb, js, args, config)
        all_ok = all_ok and ok

    print(f"\n{'=' * 64}")
    if all_ok:
        if args.restore:
            print("[OK] Restore completed. Restart Antigravity.")
        elif args.check:
            print("[OK] All installations are patchable or already patched.")
        else:
            print("[OK] Patch completed. Restart Antigravity.")
    else:
        print("[WARN] Completed with errors. Check the messages above.")
    print("=" * 64)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
