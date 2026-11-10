// src/extension.ts

import * as vscode from 'vscode';
import { spawn } from 'node:child_process';
import * as path from 'node:path';

import { CodeSearchEngine } from './codeSearch';
import { SearchResult } from './codeSearch';

let searchEngine: CodeSearchEngine;


export async function activate(context: vscode.ExtensionContext) {

    console.log('AI Dev Assistant is now active!');

    // Register the explain code command
    let explainCommand = vscode.commands.registerCommand(
        'aiAssistant.explainCode',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }
            const selection = editor.selection;
            const code = editor.document.getText(selection);
            if (!code) {
                vscode.window.showInformationMessage('Please select code to explain');
                return;
            }
            // Show loading message
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "AI is analyzing your code...",
                cancellable: false
            }, async (progress) => {
                const explanation = await callPythonAI('explain', code);
                // Create output channel
                const outputChannel = vscode.window.createOutputChannel('AI Explanation');
                outputChannel.clear();
                outputChannel.appendLine('=== Code Explanation ===\n');
                outputChannel.appendLine(explanation);
                outputChannel.show();
            });
        }
    );
    context.subscriptions.push(explainCommand);


    // Initialize the code search engine
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0].uri.fsPath;

    if (workspaceRoot) {

        const indexPath = path.join(context.globalStorageUri.fsPath,
            'code-index.json'
        );

        searchEngine = await CodeSearchEngine.create(indexPath);

        // Index codebase in background
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Window,
            title: "Indexing codebase for AI search..."
        }, async () => {
            await searchEngine.indexCodebase(workspaceRoot);
        });
    }

    // Add search command
    let searchCommand = vscode.commands.registerCommand(
        'aiAssistant.searchCode',
        async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'What are you looking for?',
                placeHolder: 'e.g., function to process user data'
            });
            if (!query) return;

            const results: SearchResult[] = await searchEngine.search(query);
            // Show results in quick pick
            const items = results.map((r: SearchResult) => ({
                label: r.snippet.split('\n')[0],
                description: r.filePath,
                detail: `Relevance: ${(r.score * 100).toFixed(1)}%`,
                snippet: r.snippet,
                filePath: r.filePath
            }));
            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select a code snippet'
            });
            if (selected) {
                // Open the file and navigate to the code
                const doc = await vscode.workspace.openTextDocument(selected.filePath);
                await vscode.window.showTextDocument(doc);
            }
        }
    );
    context.subscriptions.push(searchCommand);
}


async function callPythonAI(action: string, code: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const pythonPath = 'python3';
        const scriptPath = path.join(__dirname, '..', 'src', 'bridge.py');
        const python = spawn(pythonPath, [scriptPath, action, code]);
        let result = '';
        python.stdout.on('data', (data) => {
            result += data.toString();
        });
        python.stderr.on('data', (data) => {
            console.error(`Python error: ${data}`);
        });
        python.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python process exited with code ${code}`));
            } else {
                resolve(result);
            }
        });
    });
}