"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
function findCli() {
    if ((0, child_process_1.spawnSync)('python', ['-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'python', args: ['-m', 'scrub_ai.cli'] };
    }
    if ((0, child_process_1.spawnSync)('python3', ['-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'python3', args: ['-m', 'scrub_ai.cli'] };
    }
    if ((0, child_process_1.spawnSync)('wsl', ['python3', '-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'wsl', args: ['python3', '-m', 'scrub_ai.cli'] };
    }
    return null;
}
async function ensureCli() {
    const found = findCli();
    if (found) {
        return found;
    }
    const choice = await vscode.window.showInformationMessage('scrub-ai CLI not found. Install it now?', 'Install', 'Cancel');
    if (choice !== 'Install') {
        throw new Error('scrub-ai not installed.');
    }
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'Installing scrub-ai...', cancellable: false }, () => new Promise((resolve, reject) => {
        const proc = (0, child_process_1.spawn)('pip', ['install', 'scrub-ai'], { shell: true });
        proc.on('close', code => code === 0 ? resolve() : reject(new Error('pip install failed')));
    }));
    const after = findCli();
    if (!after) {
        throw new Error('scrub-ai installed but not found on PATH. Please restart VS Code.');
    }
    return after;
}
function runScrubAi(input, cli) {
    return new Promise((resolve, reject) => {
        const proc = (0, child_process_1.spawn)(cli.cmd, cli.args, { shell: true });
        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d) => stdout += d.toString());
        proc.stderr.on('data', (d) => stderr += d.toString());
        proc.on('error', reject);
        proc.on('close', code => code === 0 || stdout ? resolve(stdout) : reject(new Error(stderr)));
        proc.stdin.end(input);
    });
}
async function sanitizeText(original) {
    let cli;
    let sanitized;
    try {
        cli = await ensureCli();
        sanitized = await runScrubAi(original, cli);
    }
    catch (err) {
        vscode.window.showErrorMessage(`scrub-ai: ${err.message}`);
        return;
    }
    if (sanitized === original) {
        vscode.window.showInformationMessage('scrub-ai: nothing sensitive found.');
        return;
    }
    const choice = await vscode.window.showInformationMessage('scrub-ai found sensitive content. Apply changes?', { modal: false }, 'Show Diff', 'Apply', 'Cancel');
    if (choice === 'Show Diff') {
        const originalDoc = await vscode.workspace.openTextDocument({ content: original, language: 'plaintext' });
        const sanitizedDoc = await vscode.workspace.openTextDocument({ content: sanitized, language: 'plaintext' });
        await vscode.commands.executeCommand('vscode.diff', originalDoc.uri, sanitizedDoc.uri, 'scrub-ai: Before ↔ After');
        const applyChoice = await vscode.window.showInformationMessage('Apply the sanitized version?', 'Apply', 'Cancel');
        if (applyChoice !== 'Apply') {
            return;
        }
    }
    else if (choice !== 'Apply') {
        return;
    }
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return;
    }
    await editor.edit(editBuilder => {
        const selection = editor.selection;
        if (!selection.isEmpty) {
            editBuilder.replace(selection, sanitized);
        }
        else {
            const fullRange = new vscode.Range(editor.document.positionAt(0), editor.document.positionAt(editor.document.getText().length));
            editBuilder.replace(fullRange, sanitized);
        }
    });
    vscode.window.showInformationMessage('scrub-ai: sensitive content masked.');
}
function activate(context) {
    let watcherProcess = null;
    async function startWatcher() {
        try {
            const cli = await ensureCli();
            const args = [...cli.args, '--watch'];
            watcherProcess = (0, child_process_1.spawn)(cli.cmd, args, { shell: true });
            watcherProcess.on('error', () => { watcherProcess = null; });
            watcherProcess.on('close', () => { watcherProcess = null; });
        }
        catch {
            // CLI not available — watcher won't run, manual commands still work
        }
    }
    startWatcher();
    context.subscriptions.push({
        dispose: () => {
            if (watcherProcess) {
                watcherProcess.kill();
                watcherProcess = null;
            }
        }
    });
    context.subscriptions.push(vscode.commands.registerCommand('scrub-ai.sanitize', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('scrub-ai: no active editor');
            return;
        }
        const selection = editor.selection;
        const text = selection.isEmpty
            ? editor.document.getText()
            : editor.document.getText(selection);
        await sanitizeText(text);
    }), vscode.commands.registerCommand('scrub-ai.sanitizeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        await sanitizeText(editor.document.getText());
    }));
}
function deactivate() { }
//# sourceMappingURL=extension.js.map