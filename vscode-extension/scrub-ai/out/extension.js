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
const SCANNABLE_EXTENSIONS = new Set([
    '.env', '.log', '.txt', '.yaml', '.yml', '.json', '.toml', '.ini',
    '.config', '.ts', '.tsx', '.js', '.jsx', '.py', '.sh', '.md', '.xml',
    '.properties', '.cfg', '.conf', '.tf', '.hcl', '.sql'
]);
const IGNORED_DIRS = new Set(['node_modules', '.git', 'dist', 'build', 'out', '.venv', '__pycache__']);
const MAX_FILE_SIZE = 500 * 1024;
function tryCmd(cmd, args) {
    try {
        return (0, child_process_1.spawnSync)(cmd, args, { shell: false, timeout: 5000 }).status === 0;
    }
    catch {
        return false;
    }
}
function findCli() {
    const home = process.env.HOME ?? process.env.USERPROFILE ?? '';
    // On Windows the extension host may run on Windows side — route through wsl.exe
    if (process.platform === 'win32') {
        const wslPaths = [
            '/home/ubuntu/scrub-ai/.venv/bin/python3',
            `${home.replace(/\\/g, '/')}/scrub-ai/.venv/bin/python3`,
        ];
        for (const p of wslPaths) {
            if (tryCmd('wsl', [p, '-m', 'scrub_ai.cli', '--help'])) {
                return { cmd: 'wsl', args: [p, '-m', 'scrub_ai.cli'] };
            }
        }
        if (tryCmd('wsl', ['python3', '-m', 'scrub_ai.cli', '--help'])) {
            return { cmd: 'wsl', args: ['python3', '-m', 'scrub_ai.cli'] };
        }
        return null;
    }
    // Linux (including WSL extension host) / macOS
    const venvPaths = [
        `${home}/scrub-ai/.venv/bin/python3`,
        `${home}/.venv/bin/python3`,
    ];
    for (const p of venvPaths) {
        if (tryCmd(p, ['-m', 'scrub_ai.cli', '--help'])) {
            return { cmd: p, args: ['-m', 'scrub_ai.cli'] };
        }
    }
    for (const py of ['python3', 'python']) {
        if (tryCmd(py, ['-m', 'scrub_ai.cli', '--help'])) {
            return { cmd: py, args: ['-m', 'scrub_ai.cli'] };
        }
    }
    return null;
}
async function ensureCli() {
    const found = findCli();
    if (found) {
        return found;
    }
    const msg = 'scrub-ai CLI not found. Run: pip install scrub-ai (inside WSL if on Windows), then reload VS Code.';
    vscode.window.showErrorMessage(msg);
    throw new Error(msg);
}
async function ensureXclip() {
    if (process.platform !== 'linux') {
        return;
    }
    if (tryCmd('xclip', ['-version'])) {
        return;
    }
    const choice = await vscode.window.showInformationMessage('scrub-ai watch mode needs xclip. Install it now?', 'Install', 'Skip');
    if (choice !== 'Install') {
        return;
    }
    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'Installing xclip...', cancellable: false }, () => new Promise((resolve, reject) => {
        (0, child_process_1.spawn)('sudo', ['apt-get', 'install', '-y', 'xclip'], { shell: true })
            .on('close', code => code === 0 ? resolve() : reject(new Error('xclip install failed')));
    }));
}
function runScrubAi(input, cli, extraArgs = []) {
    return new Promise((resolve, reject) => {
        const proc = (0, child_process_1.spawn)(cli.cmd, [...cli.args, ...extraArgs], { shell: false });
        let stdout = '', stderr = '';
        proc.stdout.on('data', (d) => stdout += d.toString());
        proc.stderr.on('data', (d) => stderr += d.toString());
        proc.on('error', reject);
        proc.on('close', code => code === 0 || stdout ? resolve({ stdout, stderr }) : reject(new Error(stderr)));
        proc.stdin.end(input);
    });
}
function shouldScanDocument(doc) {
    if (doc.uri.scheme !== 'file') {
        return false;
    }
    const path = doc.uri.path;
    const ext = path.substring(path.lastIndexOf('.'));
    if (!SCANNABLE_EXTENSIONS.has(ext)) {
        return false;
    }
    const parts = doc.uri.fsPath.split(/[\\/]/);
    if (parts.some(p => IGNORED_DIRS.has(p))) {
        return false;
    }
    return true;
}
async function scanDocument(doc, diagnostics, cli) {
    if (!shouldScanDocument(doc)) {
        return;
    }
    const text = doc.getText();
    if (Buffer.byteLength(text) > MAX_FILE_SIZE) {
        return;
    }
    let matches = [];
    try {
        const { stderr } = await runScrubAi(text, cli, ['--dry-run', '--json']);
        const jsonLine = stderr.trim().split('\n').find(l => l.trimStart().startsWith('['));
        if (!jsonLine) {
            diagnostics.set(doc.uri, []);
            return;
        }
        matches = JSON.parse(jsonLine);
    }
    catch {
        return;
    }
    diagnostics.set(doc.uri, matches.map(m => {
        const range = new vscode.Range(doc.positionAt(m.start), doc.positionAt(m.end));
        const diag = new vscode.Diagnostic(range, `scrub-ai [${m.label}]: will be masked as ${m.replacement}`, vscode.DiagnosticSeverity.Warning);
        diag.source = 'scrub-ai';
        diag.code = m.label;
        diag.replacement = m.replacement;
        return diag;
    }));
}
class ScrubAiCodeActionProvider {
    diagnostics;
    constructor(diagnostics) {
        this.diagnostics = diagnostics;
    }
    provideCodeActions(doc, range) {
        const fileDiags = this.diagnostics.get(doc.uri) ?? [];
        const actions = [];
        for (const diag of fileDiags) {
            if (!diag.range.intersection(range)) {
                continue;
            }
            const replacement = diag.replacement;
            if (!replacement) {
                continue;
            }
            const action = new vscode.CodeAction(`Mask ${diag.code} → ${replacement}`, vscode.CodeActionKind.QuickFix);
            action.diagnostics = [diag];
            action.edit = new vscode.WorkspaceEdit();
            action.edit.replace(doc.uri, diag.range, replacement);
            action.isPreferred = true;
            actions.push(action);
        }
        if (fileDiags.filter(d => d.range.intersection(range)).length > 1) {
            const fixAll = new vscode.CodeAction('Mask all sensitive values in file', vscode.CodeActionKind.QuickFix);
            fixAll.edit = new vscode.WorkspaceEdit();
            for (const d of fileDiags) {
                const rep = d.replacement;
                if (rep) {
                    fixAll.edit.replace(doc.uri, d.range, rep);
                }
            }
            actions.push(fixAll);
        }
        return actions;
    }
}
async function sanitizeText(original, cli) {
    let sanitized;
    try {
        const { stdout } = await runScrubAi(original, cli);
        sanitized = stdout;
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
        if (await vscode.window.showInformationMessage('Apply the sanitized version?', 'Apply', 'Cancel') !== 'Apply') {
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
    await editor.edit(eb => {
        const sel = editor.selection;
        if (!sel.isEmpty) {
            eb.replace(sel, sanitized);
        }
        else {
            eb.replace(new vscode.Range(editor.document.positionAt(0), editor.document.positionAt(editor.document.getText().length)), sanitized);
        }
    });
    vscode.window.showInformationMessage('scrub-ai: sensitive content masked.');
}
function activate(context) {
    const diagnostics = vscode.languages.createDiagnosticCollection('scrub-ai');
    context.subscriptions.push(diagnostics);
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(shield) scrub-ai';
    statusBar.tooltip = 'scrub-ai: initializing...';
    statusBar.show();
    context.subscriptions.push(statusBar);
    let cli = null;
    let watcherProcess = null;
    async function init() {
        try {
            cli = await ensureCli();
            statusBar.text = '$(shield) scrub-ai';
            statusBar.tooltip = `scrub-ai active — using ${cli.cmd}`;
            statusBar.backgroundColor = undefined;
        }
        catch {
            statusBar.text = '$(warning) scrub-ai';
            statusBar.tooltip = 'scrub-ai CLI not found — click for help';
            statusBar.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            return;
        }
        await ensureXclip();
        watcherProcess = (0, child_process_1.spawn)(cli.cmd, [...cli.args, '--watch'], { shell: false });
        watcherProcess.on('error', () => { watcherProcess = null; });
        watcherProcess.on('close', () => { watcherProcess = null; });
        for (const doc of vscode.workspace.textDocuments) {
            scanDocument(doc, diagnostics, cli);
        }
    }
    init();
    context.subscriptions.push({ dispose: () => { watcherProcess?.kill(); } });
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(doc => { if (cli) {
        scanDocument(doc, diagnostics, cli);
    } }), vscode.workspace.onDidSaveTextDocument(doc => { if (cli) {
        scanDocument(doc, diagnostics, cli);
    } }), vscode.workspace.onDidCloseTextDocument(doc => { diagnostics.delete(doc.uri); }));
    context.subscriptions.push(vscode.languages.registerCodeActionsProvider({ scheme: 'file' }, new ScrubAiCodeActionProvider(diagnostics), { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }));
    context.subscriptions.push(vscode.commands.registerCommand('scrub-ai.sanitize', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('scrub-ai: no active editor');
            return;
        }
        const resolvedCli = cli ?? await ensureCli().catch(() => null);
        if (!resolvedCli) {
            return;
        }
        const sel = editor.selection;
        await sanitizeText(sel.isEmpty ? editor.document.getText() : editor.document.getText(sel), resolvedCli);
    }), vscode.commands.registerCommand('scrub-ai.sanitizeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        const resolvedCli = cli ?? await ensureCli().catch(() => null);
        if (!resolvedCli) {
            return;
        }
        await sanitizeText(editor.document.getText(), resolvedCli);
    }));
}
function deactivate() { }
//# sourceMappingURL=extension.js.map