const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');

const { createServer, readEntries, writeEntries } = require('../server');

function createTempDataFile() {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'csarchive-'));
  const dataPath = path.join(tempDir, 'entries.json');
  fs.writeFileSync(dataPath, '[]\n', 'utf8');
  return { tempDir, dataPath };
}

(async () => {
  const temp = createTempDataFile();
  const originalCwd = process.cwd();
  process.chdir(temp.tempDir);

  const server = createServer();
  server.listen(0, '127.0.0.1', () => {
    const { port } = server.address();

    const req = http.request({
      hostname: '127.0.0.1',
      port,
      path: '/api/entries',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        const payload = JSON.parse(body);
        assert.strictEqual(res.statusCode, 201);
        assert.strictEqual(payload.entry.week, '1');
        server.close(() => {
          process.chdir(originalCwd);
          console.log('Node tests passed');
        });
      });
    });

    req.write(JSON.stringify({ week: '1', reflection: '좋았다.' }));
    req.end();
  });
})();
