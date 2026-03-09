const vscode = require('vscode');
const http = require('http');

let statusBarItem = null;
let isActive = false;
let cdpSockets = [];
let sessionStats = { retries: 0, continues: 0, runs: 0, rateLimitWaits: 0 };
let rateLimitCountdown = null;

function getConfig() {
    const config = vscode.workspace.getConfiguration('autopilot');
    return {
        autoRetry: config.get('autoRetry', true),
        autoContinue: config.get('autoContinue', true),
        autoRun: config.get('autoRun', false),
        runBlocklist: config.get('runBlocklist', [
            'rm -rf', 'rm -r', 'sudo', 'drop ', 'delete ', 'format ',
            'mkfs', 'shutdown', 'reboot', 'kill -9', 'truncate',
            ':>', '> /dev', 'dd if=', 'chmod 777', 'chown'
        ]),
        rateLimitHandler: config.get('rateLimitHandler', true),
        showStats: config.get('showStats', true),
        cdpPort: config.get('cdpPort', 0),
        enabled: config.get('enabled', true)
    };
}

function buildInjectionScript(config) {
    return `
(function() {
    if (window.__autopilotInjected) return;
    window.__autopilotInjected = true;

    const CONFIG = ${JSON.stringify(config)};
    const stats = { retries: 0, continues: 0, runs: 0, rateLimitWaits: 0 };
    let lastClickTime = 0;
    let rateLimitActive = false;
    const COOLDOWN = 2500;
    const CHECK_INTERVAL = 1500;

    const RETRY_TEXTS = ['retry', 'try again', 'riprova', 'riprovare'];
    const CONTINUE_TEXTS = ['continue', 'continua', 'proceed', 'yes', 'continue generating', 'keep going'];
    const RUN_TEXTS = ['run', 'run command', 'execute', 'run in terminal', 'esegui'];
    const RATE_LIMIT_PATTERNS = [
        'rate limit', 'too many requests', 'try again in', 'try again later',
        'limite di frequenza', 'limit reached', 'quota exceeded', 'throttled',
        'please wait', 'slow down'
    ];

    function isVisible(el) {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && el.offsetParent !== null;
    }

    function isClickable(el) {
        if (!el) return false;
        return !el.disabled && el.getAttribute('aria-disabled') !== 'true' && isVisible(el);
    }

    function findButton(doc, textList) {
        if (!doc) return null;
        const selectors = ['button', '[role="button"]', 'a', '.monaco-button', '.action-label'];
        for (const selector of selectors) {
            try {
                const elements = doc.querySelectorAll(selector);
                for (const el of elements) {
                    const text = (el.textContent || '').trim().toLowerCase();
                    if (textList.some(t => text === t || text.startsWith(t)) && isClickable(el)) return el;
                }
            } catch (e) {}
        }
        return null;
    }

    function getCommandText(btnEl) {
        try {
            let node = btnEl.parentElement;
            for (let i = 0; i < 5 && node; i++) {
                const codeBlock = node.querySelector('pre, code, .monaco-editor, [class*="code-block"]');
                if (codeBlock) return (codeBlock.textContent || '').trim().toLowerCase();
                node = node.parentElement;
            }
            const prev = btnEl.previousElementSibling;
            if (prev) {
                const code = prev.querySelector('pre, code');
                if (code) return (code.textContent || '').trim().toLowerCase();
            }
        } catch (e) {}
        return '';
    }

    function isCommandSafe(cmdText) {
        if (!cmdText) return true;
        const lower = cmdText.toLowerCase();
        for (const blocked of CONFIG.runBlocklist) {
            if (lower.includes(blocked.toLowerCase())) return false;
        }
        return true;
    }

    function detectRateLimit(doc) {
        if (!doc) return null;
        try {
            const body = (doc.body?.textContent || '').toLowerCase();
            for (const pattern of RATE_LIMIT_PATTERNS) {
                if (body.includes(pattern)) {
                    const match = body.match(/(?:try again in|wait|attendi)\\s*(\\d+)\\s*(?:second|sec|s)/i);
                    return { detected: true, waitSeconds: match ? parseInt(match[1], 10) : 15 };
                }
            }
        } catch (e) {}
        return null;
    }

    function clickWithCooldown(el, actionType) {
        const now = Date.now();
        if (now - lastClickTime < COOLDOWN) return false;
        lastClickTime = now;
        stats[actionType]++;
        el.click();
        console.log('[Autopilot] ' + actionType + ' (#' + stats[actionType] + ')');
        window.__autopilotStats = JSON.stringify(stats);
        return true;
    }

    function check() {
        try {
            const frame = document.getElementById('antigravity.agentPanel');
            if (!frame) return;
            const doc = frame.contentDocument;
            if (!doc || doc.readyState !== 'complete') return;

            if (rateLimitActive) return;

            // Rate Limit detection (highest priority)
            if (CONFIG.rateLimitHandler) {
                const rateLimit = detectRateLimit(doc);
                if (rateLimit && rateLimit.detected) {
                    rateLimitActive = true;
                    stats.rateLimitWaits++;
                    window.__autopilotStats = JSON.stringify(stats);
                    const waitMs = rateLimit.waitSeconds * 1000 + 2000;
                    console.log('[Autopilot] Rate limit detected. Waiting ' + rateLimit.waitSeconds + 's...');
                    window.__autopilotRateLimit = rateLimit.waitSeconds;
                    setTimeout(() => {
                        rateLimitActive = false;
                        window.__autopilotRateLimit = 0;
                        console.log('[Autopilot] Rate limit wait complete. Resuming.');
                        const retryBtn = findButton(doc, RETRY_TEXTS);
                        if (retryBtn) clickWithCooldown(retryBtn, 'retries');
                    }, waitMs);
                    return;
                }
            }

            // Auto-Retry
            if (CONFIG.autoRetry) {
                const retryBtn = findButton(doc, RETRY_TEXTS);
                if (retryBtn) {
                    clickWithCooldown(retryBtn, 'retries');
                    return;
                }
            }

            // Auto-Continue
            if (CONFIG.autoContinue) {
                const continueBtn = findButton(doc, CONTINUE_TEXTS);
                if (continueBtn) {
                    clickWithCooldown(continueBtn, 'continues');
                    return;
                }
            }

            // Auto-Run (with safety check)
            if (CONFIG.autoRun) {
                const runBtn = findButton(doc, RUN_TEXTS);
                if (runBtn) {
                    const cmdText = getCommandText(runBtn);
                    if (isCommandSafe(cmdText)) {
                        clickWithCooldown(runBtn, 'runs');
                    } else {
                        console.log('[Autopilot] BLOCKED unsafe command: ' + cmdText.substring(0, 80));
                    }
                    return;
                }
            }
        } catch (e) {}
    }

    window.__autopilotInterval = setInterval(check, CHECK_INTERVAL);
    window.__autopilotStats = JSON.stringify(stats);
    console.log('[Autopilot] Injected | retry=' + CONFIG.autoRetry + ' continue=' + CONFIG.autoContinue + ' run=' + CONFIG.autoRun + ' rateLimit=' + CONFIG.rateLimitHandler);
})();
`;
}

async function findCDPPort() {
    const config = getConfig();
    const standardPorts = [9222, 9000, 9001, 9002, 9003];

    // Try custom port first
    if (config.cdpPort > 0) {
        try {
            if (await checkPort(config.cdpPort)) return config.cdpPort;
        } catch (e) { }
        console.log(`[Autopilot] Custom port ${config.cdpPort} not responding, trying standard ports...`);
    }

    // Always fallback to standard ports
    for (const port of standardPorts) {
        try {
            if (await checkPort(port)) return port;
        } catch (e) { }
    }
    return null;
}

function checkPort(port) {
    return new Promise((resolve) => {
        const timeout = setTimeout(() => resolve(false), 1000);
        const req = http.get(`http://127.0.0.1:${port}/json/version`, (res) => {
            clearTimeout(timeout);
            resolve(res.statusCode === 200);
        });
        req.on('error', () => { clearTimeout(timeout); resolve(false); });
        req.setTimeout(1000, () => { req.destroy(); resolve(false); });
    });
}

function getCDPTargets(port) {
    return new Promise((resolve) => {
        const timeout = setTimeout(() => resolve([]), 2000);
        const req = http.get(`http://127.0.0.1:${port}/json/list`, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                clearTimeout(timeout);
                try { resolve(JSON.parse(data)); } catch (e) { resolve([]); }
            });
        });
        req.on('error', () => { clearTimeout(timeout); resolve([]); });
    });
}

function getAllValidTargets(targets) {
    return targets.filter(t =>
        t.type === 'page' &&
        t.webSocketDebuggerUrl &&
        !t.title?.toLowerCase().includes('launchpad') &&
        !t.url?.includes('jetski')
    );
}

async function injectIntoTarget(target, config) {
    return new Promise((resolve) => {
        try {
            const WebSocket = require('ws');
            const ws = new WebSocket(target.webSocketDebuggerUrl);
            ws.on('open', () => {
                ws.send(JSON.stringify({
                    id: 1,
                    method: 'Runtime.evaluate',
                    params: { expression: buildInjectionScript(config), includeCommandLineAPI: true }
                }));
                ws.on('message', (data) => {
                    try {
                        const response = JSON.parse(data.toString());
                        if (response.id === 1) {
                            cdpSockets.push(ws);
                            resolve(true);
                        }
                    } catch (e) { }
                });
            });
            ws.on('error', () => resolve(false));
            setTimeout(() => resolve(false), 5000);
        } catch (e) {
            resolve(false);
        }
    });
}

async function pollStats() {
    if (!isActive || cdpSockets.length === 0) return;
    for (const ws of cdpSockets) {
        try {
            if (ws.readyState !== 1) continue;
            ws.send(JSON.stringify({
                id: 100,
                method: 'Runtime.evaluate',
                params: { expression: 'window.__autopilotStats || "{}"' }
            }));
        } catch (e) { }
    }
}

async function injectViaCDP() {
    try {
        const port = await findCDPPort();
        if (!port) return false;

        const targets = await getCDPTargets(port);
        const validTargets = getAllValidTargets(targets);
        if (!validTargets.length) return false;

        const config = getConfig();
        const results = await Promise.all(validTargets.map(t => injectIntoTarget(t, config)));
        const successCount = results.filter(r => r).length;

        if (successCount > 0) {
            console.log(`[Autopilot] Injected into ${successCount}/${validTargets.length} windows`);

            // Listen for stat updates
            for (const ws of cdpSockets) {
                ws.on('message', (data) => {
                    try {
                        const msg = JSON.parse(data.toString());
                        if (msg.id === 100 && msg.result?.result?.value) {
                            const parsed = JSON.parse(msg.result.result.value);
                            if (parsed.retries !== undefined) {
                                sessionStats = { ...sessionStats, ...parsed };
                                updateStatusBar();
                            }
                        }
                    } catch (e) { }
                });
            }

            return successCount;
        }
        return false;
    } catch (e) {
        return false;
    }
}

let statsInterval = null;

function updateStatusBar() {
    if (!statusBarItem) return;
    const config = getConfig();

    if (isActive) {
        const features = [];
        if (config.autoRetry) features.push('Retry');
        if (config.autoContinue) features.push('Continue');
        if (config.autoRun) features.push('Run');
        if (config.rateLimitHandler) features.push('RateLimit');

        statusBarItem.text = '$(rocket) Autopilot: ON';

        let tooltip = 'Autopilot is active (' + features.join(', ') + ')';
        if (config.showStats) {
            const total = sessionStats.retries + sessionStats.continues + sessionStats.runs + sessionStats.rateLimitWaits;
            if (total > 0) {
                tooltip += '\n\nSession: ';
                const parts = [];
                if (sessionStats.retries) parts.push(sessionStats.retries + ' retries');
                if (sessionStats.continues) parts.push(sessionStats.continues + ' continues');
                if (sessionStats.runs) parts.push(sessionStats.runs + ' runs');
                if (sessionStats.rateLimitWaits) parts.push(sessionStats.rateLimitWaits + ' rate waits');
                tooltip += parts.join(', ');
            }
        }
        tooltip += '\n\nManage via Extensions panel or Command Palette.';
        statusBarItem.tooltip = tooltip;
    } else {
        statusBarItem.text = '$(circle-slash) Autopilot: OFF';
        statusBarItem.tooltip = 'Autopilot is disabled. Enable via Extensions panel or Command Palette.';
    }
}

async function startAutopilot(context, attempt) {
    const MAX_RETRIES = 5;
    const currentAttempt = attempt || 1;

    isActive = true;
    sessionStats = { retries: 0, continues: 0, runs: 0, rateLimitWaits: 0 };
    updateStatusBar();

    const windowCount = await injectViaCDP();
    if (windowCount) {
        const config = getConfig();
        const features = [];
        if (config.autoRetry) features.push('Retry');
        if (config.autoContinue) features.push('Continue');
        if (config.autoRun) features.push('Run');
        if (config.rateLimitHandler) features.push('Rate Limit');

        vscode.window.showInformationMessage(
            `🚀 Autopilot: Active (${windowCount} window${windowCount > 1 ? 's' : ''}) | ${features.join(', ')}`
        );

        statsInterval = setInterval(pollStats, 5000);
    } else if (currentAttempt < MAX_RETRIES) {
        const delayMs = Math.pow(2, currentAttempt) * 1000;
        console.log(`[Autopilot] CDP not ready, retry ${currentAttempt}/${MAX_RETRIES} in ${delayMs / 1000}s...`);
        statusBarItem.text = '$(sync~spin) Autopilot: Connecting...';
        statusBarItem.tooltip = `Waiting for CDP (attempt ${currentAttempt}/${MAX_RETRIES})`;
        setTimeout(() => startAutopilot(context, currentAttempt + 1), delayMs);
    } else {
        isActive = false;
        updateStatusBar();
        vscode.window.showErrorMessage(
            '❌ Autopilot: CDP not available after ' + MAX_RETRIES + ' attempts. Launch Antigravity with --remote-debugging-port=9222'
        );
    }
}

function stopAutopilot() {
    isActive = false;

    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }

    for (const ws of cdpSockets) {
        try {
            ws.send(JSON.stringify({
                id: 999,
                method: 'Runtime.evaluate',
                params: {
                    expression: `
                        if(window.__autopilotInterval) clearInterval(window.__autopilotInterval);
                        window.__autopilotInjected = false;
                        window.__autopilotStats = null;
                        window.__autopilotRateLimit = 0;
                    `
                }
            }));
            ws.close();
        } catch (e) { }
    }
    cdpSockets = [];

    updateStatusBar();
    vscode.window.showInformationMessage('⏹️ Autopilot: Stopped');
}

function showStats() {
    const config = getConfig();
    const total = sessionStats.retries + sessionStats.continues + sessionStats.runs + sessionStats.rateLimitWaits;
    const status = isActive ? 'ACTIVE' : 'STOPPED';
    const windows = cdpSockets.filter(ws => ws.readyState === 1).length;

    let msg = `Autopilot: ${status} | ${windows} window${windows !== 1 ? 's' : ''}`;
    msg += ` | Features: ${config.autoRetry ? '✓' : '✗'}Retry ${config.autoContinue ? '✓' : '✗'}Continue ${config.autoRun ? '✓' : '✗'}Run ${config.rateLimitHandler ? '✓' : '✗'}RateLimit`;
    if (total > 0) {
        msg += ` | Actions: ${sessionStats.retries}R ${sessionStats.continues}C ${sessionStats.runs}X ${sessionStats.rateLimitWaits}W`;
    }

    vscode.window.showInformationMessage(msg);
}

function activate(context) {
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    context.subscriptions.push(statusBarItem);
    statusBarItem.show();

    context.subscriptions.push(
        vscode.commands.registerCommand('autopilot.start', () => startAutopilot(context)),
        vscode.commands.registerCommand('autopilot.stop', stopAutopilot),
        vscode.commands.registerCommand('autopilot.stats', showStats)
    );

    const config = getConfig();
    if (config.enabled) {
        setTimeout(() => startAutopilot(context), 5000);
    }

    updateStatusBar();
}

function deactivate() {
    stopAutopilot();
}

module.exports = { activate, deactivate };
