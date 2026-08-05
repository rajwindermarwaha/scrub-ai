import * as vscode from 'vscode';
import { spawn, spawnSync } from 'child_process';

const SCANNABLE_EXTENSIONS = new Set([
    '.env', '.log', '.txt', '.yaml', '.yml', '.json', '.toml', '.ini',
    '.config', '.ts', '.tsx', '.js', '.jsx', '.py', '.sh', '.md', '.xml',
    '.properties', '.cfg', '.conf', '.tf', '.hcl', '.sql'
]);

const IGNORED_DIRS = new Set(['node_modules', '.git', 'dist', 'build', 'out', '.venv', '__pycache__']);
const MAX_FILE_SIZE = 500 * 1024; // 500 KB

interface CliMatch {
    start: number;
    end: number;
    original: string;
    replacement: string;
    label: string;
    confidence: number;
}

function findCli(): { cmd: string; args: string[] } | null {
    // Common venv locations to probe
    const venvCandidates = [
        `${process.env.HOME}/.venv/bin/python3`,
        `${process.env.HOME}/scrub-ai/.venv/bin/python3`,
        `${process.env.HOME}/.local/bin/python3`,
    ];
    for (const p of venvCandidates) {
        if (spawnSync(p, ['-m', 'scrub_ai.cli', '--help'], { shell: false }).status === 0) {
            return { cmd: p, args: ['-m', 'scrub_ai.cli'] };
        }
    }
    if (spawnSync('python3', ['-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'python3', args: ['-m', 'scrub_ai.cli'] };
    }
    if (spawnSync('python', ['-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'python', args: ['-m', 'scrub_ai.cli'] };
    }
    if (process.platform === 'win32' &&
        spawnSync('wsl', ['python3', '-m', 'scrub_ai.cli', '--help'], { shell: true }).status === 0) {
        return { cmd: 'wsl', args: ['python3', '-m', 'scrub_ai.cli'] };
    }
    return null;
}

async function ensureCli(): Promise<{ cmd: string; args: string[] }> {
    const found = findCli();
    if (found) { return found; }

    const choice = await vscode.window.showInformationMessage(
        'scrub-ai CLI not found. Install it now?',
        'Install', 'Cancel'
    );
    if (choice !== 'Install') { throw new Error('scrub-ai not installed.'); }

    const pipCmd = spawnSync('pip', ['--version'], { shell: true }).status === 0 ? 'pip' : 'pip3';
    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Installing scrub-ai...', cancellable: false },
        () => new Promise<void>((resolve, reject) => {
            const proc = spawn(pipCmd, ['install', 'scrub-ai'], { shell: true });
            proc.on('close', code => code === 0 ? resolve() : reject(new Error(`${pipCmd} install failed`)));
        })
    );

    const after = findCli();
    if (!after) { throw new Error('scrub-ai installed but not found on PATH. Please restart VS Code.'); }
    return after;
}

async function ensureXclip(): Promise<void> {
    if (process.platform !== 'linux') { return; }
    if (spawnSync('xclip', ['-version'], { shell: true }).status === 0) { return; }

    const choice = await vscode.window.showInformationMessage(
        'scrub-ai watch mode needs xclip for clipboard access on Linux. Install it now?',
        'Install', 'Skip'
    );
    if (choice !== 'Install') { return; }

    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Installing xclip...', cancellable: false },
        () => new Promise<void>((resolve, reject) => {
            const proc = spawn('sudo', ['apt-get', 'install', '-y', 'xclip'], { shell: true });
            proc.on('close', code => code === 0 ? resolve() : reject(new Error('xclip install failed')));
        })
    );
}

function runScrubAi(input: string, cli: { cmd: string; args: string[] }, extraArgs: string[] = []): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
        const proc = spawn(cli.cmd, [...cli.args, ...extraArgs], { shell: true });
        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d: Buffer) => stdout += d.toString());
        proc.stderr.on('data', (d: Buffer) => stderr += d.toString());
        proc.on('error', reject);
        proc.on('close', code => code === 0 || stdout ? resolve({ stdout, stderr }) : reject(new Error(stderr)));
        proc.stdin.end(input);
    });
}

function shouldScanDocument(doc: vscode.TextDocument): boolean {
    if (doc.uri.scheme !== 'file') { return false; }
    const ext = doc.uri.path.substring(doc.uri.path.lastIndexOf('.'));
    if (!SCANNABLE_EXTENSIONS.has(ext)) { return false; }
    const parts = doc.uri.fsPath.split(/[\\/]/);
    if (parts.some(p => IGNORED_DIRS.has(p))) { return false; }
    return true;
}

async function scanDocument(
    doc: vscode.TextDocument,
    diagnostics: vscode.DiagnosticCollection,
    cli: { cmd: string; args: string[] }
): Promise<void> {
    if (!shouldScanDocument(doc)) { return; }

    const text = doc.getText();
    if (Buffer.byteLength(text) > MAX_FILE_SIZE) { return; }

    let matches: CliMatch[] = [];
    try {
        const { stderr } = await runScrubAi(text, cli, ['--dry-run', '--json']);
        const jsonLine = stderr.trim().split('\n').find(l => l.startsWith('['));
        if (!jsonLine) { diagnostics.set(doc.uri, []); return; }
        matches = JSON.parse(jsonLine);
    } catch {
        return;
    }

    const items: vscode.Diagnostic[] = matches.map(m => {
        const start = doc.positionAt(m.start);
        const end = doc.positionAt(m.end);
        const range = new vscode.Range(start, end);
        const diag = new vscode.Diagnostic(
            range,
            `scrub-ai: ${m.label} detected — will be masked as ${m.replacement}`,
            vscode.DiagnosticSeverity.Warning
        );
        diag.source = 'scrub-ai';
        diag.code = m.label;
        (diag as any).replacement = m.replacement;
        return diag;
    });

    diagnostics.set(doc.uri, items);
}

class ScrubAiCodeActionProvider implements vscode.CodeActionProvider {
    constructor(private diagnostics: vscode.DiagnosticCollection) {}

    provideCodeActions(doc: vscode.TextDocument, range: vscode.Range): vscode.CodeAction[] {
        const fileDiags = this.diagnostics.get(doc.uri) ?? [];
        const actions: vscode.CodeAction[] = [];

        for (const diag of fileDiags) {
            if (!diag.range.intersection(range)) { continue; }
            const replacement = (diag as any).replacement as string;
            if (!replacement) { continue; }

            const action = new vscode.CodeAction(
                `Mask ${diag.code} → ${replacement}`,
                vscode.CodeActionKind.QuickFix
            );
            action.diagnostics = [diag];
            action.edit = new vscode.WorkspaceEdit();
            action.edit.replace(doc.uri, diag.range, replacement);
            action.isPreferred = true;
            actions.push(action);
        }

        // "Fix all" action if multiple diagnostics on this line
        const lineDiags = fileDiags.filter(d => d.range.intersection(range));
        if (lineDiags.length > 1) {
            const fixAll = new vscode.CodeAction('Mask all sensitive values in file', vscode.CodeActionKind.QuickFix);
            fixAll.edit = new vscode.WorkspaceEdit();
            for (const d of fileDiags) {
                const rep = (d as any).replacement as string;
                if (rep) { fixAll.edit.replace(doc.uri, d.range, rep); }
            }
            actions.push(fixAll);
        }

        return actions;
    }
}

async function sanitizeText(original: string, cli: { cmd: string; args: string[] }): Promise<void> {
    let sanitized: string;
    try {
        const { stdout } = await runScrubAi(original, cli);
        sanitized = stdout;
    } catch (err: any) {
        vscode.window.showErrorMessage(`scrub-ai: ${err.message}`);
        return;
    }

    if (sanitized === original) {
        vscode.window.showInformationMessage('scrub-ai: nothing sensitive found.');
        return;
    }

    const choice = await vscode.window.showInformationMessage(
        'scrub-ai found sensitive content. Apply changes?',
        { modal: false },
        'Show Diff', 'Apply', 'Cancel'
    );

    if (choice === 'Show Diff') {
        const originalDoc = await vscode.workspace.openTextDocument({ content: original, language: 'plaintext' });
        const sanitizedDoc = await vscode.workspace.openTextDocument({ content: sanitized, language: 'plaintext' });
        await vscode.commands.executeCommand('vscode.diff', originalDoc.uri, sanitizedDoc.uri, 'scrub-ai: Before ↔ After');
        const applyChoice = await vscode.window.showInformationMessage('Apply the sanitized version?', 'Apply', 'Cancel');
        if (applyChoice !== 'Apply') { return; }
    } else if (choice !== 'Apply') {
        return;
    }

    const editor = vscode.window.activeTextEditor;
    if (!editor) { return; }

    await editor.edit(editBuilder => {
        const selection = editor.selection;
        if (!selection.isEmpty) {
            editBuilder.replace(selection, sanitized);
        } else {
            const fullRange = new vscode.Range(
                editor.document.positionAt(0),
                editor.document.positionAt(editor.document.getText().length)
            );
            editBuilder.replace(fullRange, sanitized);
        }
    });

    vscode.window.showInformationMessage('scrub-ai: sensitive content masked.');
}

export function activate(context: vscode.ExtensionContext) {
    const diagnostics = vscode.languages.createDiagnosticCollection('scrub-ai');
    context.subscriptions.push(diagnostics);

    let cli: { cmd: string; args: string[] } | null = null;
    let watcherProcess: ReturnType<typeof spawn> | null = null;

    async function init() {
        try {
            cli = await ensureCli();
        } catch {
            return; // CLI not available — commands will prompt again when invoked
        }

        // Start clipboard watcher
        await ensureXclip();
        const args = [...cli.args, '--watch'];
        watcherProcess = spawn(cli.cmd, args, { shell: true });
        watcherProcess.on('error', () => { watcherProcess = null; });
        watcherProcess.on('close', () => { watcherProcess = null; });

        // Scan already-open documents
        for (const doc of vscode.workspace.textDocuments) {
            scanDocument(doc, diagnostics, cli);
        }
    }

    init();

    context.subscriptions.push({ dispose: () => { watcherProcess?.kill(); } });

    // Scan on open and save
    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(doc => {
            if (cli) { scanDocument(doc, diagnostics, cli); }
        }),
        vscode.workspace.onDidSaveTextDocument(doc => {
            if (cli) { scanDocument(doc, diagnostics, cli); }
        }),
        vscode.workspace.onDidCloseTextDocument(doc => {
            diagnostics.delete(doc.uri);
        })
    );

    // Code action provider (lightbulb quick-fix)
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { scheme: 'file' },
            new ScrubAiCodeActionProvider(diagnostics),
            { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }
        )
    );

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand('scrub-ai.sanitize', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) { vscode.window.showWarningMessage('scrub-ai: no active editor'); return; }
            const resolvedCli = cli ?? await ensureCli().catch(() => null);
            if (!resolvedCli) { return; }
            const selection = editor.selection;
            const text = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
            await sanitizeText(text, resolvedCli);
        }),

        vscode.commands.registerCommand('scrub-ai.sanitizeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) { return; }
            const resolvedCli = cli ?? await ensureCli().catch(() => null);
            if (!resolvedCli) { return; }
            await sanitizeText(editor.document.getText(), resolvedCli);
        })
    );
}

export function deactivate() {}
