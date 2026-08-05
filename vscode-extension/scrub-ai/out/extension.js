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
function runScrubAi(input) {
    return new Promise((resolve, reject) => {
        const proc = (0, child_process_1.spawn)('wsl', ['/home/ubuntu/scrub-ai/.venv/bin/scrub-ai'], { shell: true });
        let stdout = '';
        let stderr = '';
        proc.stdout.on('data', (d) => stdout += d.toString());
        proc.stderr.on('data', (d) => stderr += d.toString());
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
async function sanitizeText(original) {
    let sanitized;
    try {
        sanitized = await runScrubAi(original);
    }
    catch (err) {
        vscode.window.showErrorMessage(`scrub-ai error: ${err.message}`);
        return;
    }
    if (sanitized === original) {
        vscode.window.showInformationMessage('scrub-ai: nothing sensitive found.');
        return;
    }
    const choice = await vscode.window.showInformationMessage('scrub-ai found sensitive content. Apply changes?', { modal: false }, 'Show Diff', 'Apply', 'Cancel');
    if (choice === 'Show Diff') {
        // Write to temp docs for diff view
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
    // Apply to editor
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
    vscode.window.showInformationMessage('scrub-ai extension activated!');
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