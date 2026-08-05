import * as vscode from 'vscode';
import { spawn } from 'child_process';

function runScrubAi(input: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const proc = spawn('wsl', ['/home/ubuntu/scrub-ai/.venv/bin/scrub-ai'], { shell: true });
        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d: Buffer) => stdout += d.toString());
        proc.stderr.on('data', (d: Buffer) => stderr += d.toString());
        proc.on('error', (err) => {
            console.error('scrub-ai spawn error:', err.message);
            reject(err);
        });
        proc.on('close', code => {
            code === 0 || stdout ? resolve(stdout) : reject(new Error(stderr));
        });
        proc.stdin.end(input);
    });
}

async function sanitizeText(original: string): Promise<void> {
    let sanitized: string;
    try {
        sanitized = await runScrubAi(original);
    } catch (err: any) {
        vscode.window.showErrorMessage(`scrub-ai error: ${err.message}`);
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
        // Write to temp docs for diff view
        const originalDoc = await vscode.workspace.openTextDocument({ content: original, language: 'plaintext' });
        const sanitizedDoc = await vscode.workspace.openTextDocument({ content: sanitized, language: 'plaintext' });
        await vscode.commands.executeCommand('vscode.diff', originalDoc.uri, sanitizedDoc.uri, 'scrub-ai: Before ↔ After');

        const applyChoice = await vscode.window.showInformationMessage('Apply the sanitized version?', 'Apply', 'Cancel');
        if (applyChoice !== 'Apply') { return; }
    } else if (choice !== 'Apply') {
        return;
    }

    // Apply to editor
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
    vscode.window.showInformationMessage('scrub-ai extension activated!');

    context.subscriptions.push(
        vscode.commands.registerCommand('scrub-ai.sanitize', async () => {
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
        }),

        vscode.commands.registerCommand('scrub-ai.sanitizeFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) { return; }
            await sanitizeText(editor.document.getText());
        })
    );
}

export function deactivate() {}
