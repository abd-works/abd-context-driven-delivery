import { spawn, spawnSync, type ChildProcess } from 'node:child_process';

// `npm start`: the explorer's two servers as one app, as the chat bar's status row launches it. Vite serves the page on
// the app's ports and passes /api to the web server, so the app answers only while both run; when one stops, the other
// is stopped too, so a half-started app never answers as running.
const servers: ChildProcess[] = ['npm run server', 'npm run dev'].map(command => spawn(command, { shell: true, stdio: 'inherit' }));

// Each server runs under a shell, and on Windows killing the shell leaves npm and its server running, so there the
// whole tree under the shell is stopped.
function stop(server: ChildProcess): void {
  if (server.exitCode !== null || server.pid === undefined) return;
  if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(server.pid), '/T', '/F'], { stdio: 'ignore' });
  else server.kill();
}

function stopAll(code: number): void {
  for (const server of servers) stop(server);
  process.exit(code);
}

for (const server of servers) server.on('exit', code => stopAll(code ?? 1));
process.on('SIGINT', () => stopAll(0));
process.on('SIGTERM', () => stopAll(0));
