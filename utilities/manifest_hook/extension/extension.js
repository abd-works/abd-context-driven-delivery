const vscode = require('vscode');
const http = require('http');

const PORT = 37291;
let server;

function activate(context) {
    server = http.createServer((req, res) => {
        if (req.method !== 'POST' || req.url !== '/notify') {
            res.writeHead(404);
            res.end();
            return;
        }

        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const msg = data.body ? `${data.title}: ${data.body}` : data.title;
                if (data.level === 'error') {
                    vscode.window.showErrorMessage(msg);
                } else if (data.level === 'warning') {
                    vscode.window.showWarningMessage(msg);
                } else {
                    vscode.window.showInformationMessage(msg);
                }
            } catch (_) {}
            res.writeHead(200);
            res.end('ok');
        });
    });

    server.listen(PORT, '127.0.0.1', () => {
        console.log(`manifest-gate-notifier listening on http://127.0.0.1:${PORT}`);
    });

    server.on('error', err => {
        console.error('manifest-gate-notifier: server error', err.message);
    });

    context.subscriptions.push({ dispose: () => server.close() });
}

function deactivate() {
    if (server) server.close();
}

module.exports = { activate, deactivate };
