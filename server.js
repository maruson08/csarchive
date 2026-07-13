const http = require('http');
const fs = require('fs');
const path = require('path');

const HOST = process.env.HOST || '127.0.0.1';
const PORT = Number(process.env.PORT || 3000);
const DATA_FILE = path.join(__dirname, 'data', 'entries.json');

function ensureDataFile() {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]\n', 'utf8');
  }
}

function readEntries() {
  ensureDataFile();
  const raw = fs.readFileSync(DATA_FILE, 'utf8');
  return JSON.parse(raw);
}

function writeEntries(entries) {
  ensureDataFile();
  fs.writeFileSync(DATA_FILE, JSON.stringify(entries, null, 2) + '\n', 'utf8');
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body)
  });
  res.end(body);
}

function serveFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    res.writeHead(200, {
      'Content-Type': contentType,
      'Content-Length': data.length
    });
    res.end(data);
  });
}

function parseBody(req, callback) {
  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
  });
  req.on('end', () => {
    if (!body) {
      callback({});
      return;
    }

    try {
      callback(JSON.parse(body));
    } catch {
      callback({});
    }
  });
}

function createServer() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);

    if (req.method === 'GET' && url.pathname === '/') {
      serveFile(res, path.join(__dirname, 'public', 'index.html'), 'text/html; charset=utf-8');
      return;
    }

    if (req.method === 'GET' && url.pathname === '/style.css') {
      serveFile(res, path.join(__dirname, 'public', 'style.css'), 'text/css; charset=utf-8');
      return;
    }

    if (req.method === 'GET' && url.pathname === '/app.js') {
      serveFile(res, path.join(__dirname, 'public', 'app.js'), 'application/javascript; charset=utf-8');
      return;
    }

    if (req.method === 'GET' && url.pathname === '/api/entries') {
      const entries = readEntries();
      sendJson(res, 200, { entries });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/entries') {
      parseBody(req, (body) => {
        const entry = {
          id: `week-${body.week || 'unknown'}-${Date.now()}`,
          week: body.week || '',
          colab_link: body.colab_link || '',
          reflection: body.reflection || '',
          improvement: body.improvement || ''
        };

        const entries = readEntries();
        entries.push(entry);
        writeEntries(entries);
        sendJson(res, 201, { entry, entries });
      });
      return;
    }

    res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ error: 'Not found' }));
  });
}

if (require.main === module) {
  const server = createServer();
  server.listen(PORT, HOST, () => {
    console.log(`Server running at http://${HOST}:${PORT}`);
  });
}

module.exports = { createServer, readEntries, writeEntries };
