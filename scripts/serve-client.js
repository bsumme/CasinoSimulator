#!/usr/bin/env node
const http = require('http')
const fs = require('fs')
const path = require('path')
const { URL } = require('url')

const CLIENT_ROOT = path.join(__dirname, '..', 'client')
const INDEX_FILE = path.join(CLIENT_ROOT, 'index.html')
const DEFAULT_PORT = Number(process.env.PORT || 5173)
const HOST = process.env.HOST || '0.0.0.0'

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.map': 'application/json; charset=utf-8'
}

const serveFile = (filePath, res, statusCode = 200) => {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' })
      res.end('Internal server error')
      return
    }

    const ext = path.extname(filePath)
    const contentType = MIME_TYPES[ext] || 'application/octet-stream'
    res.writeHead(statusCode, { 'Content-Type': contentType })
    res.end(data)
  })
}

const server = http.createServer((req, res) => {
  const requestUrl = new URL(req.url, `http://${req.headers.host}`)
  const decodedPath = decodeURIComponent(requestUrl.pathname)
  const safePath = decodedPath === '/' ? '/index.html' : decodedPath

  const resolvedPath = path.join(CLIENT_ROOT, safePath)

  if (!resolvedPath.startsWith(CLIENT_ROOT)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' })
    res.end('Forbidden')
    return
  }

  fs.stat(resolvedPath, (err, stats) => {
    if (!err && stats.isFile()) {
      serveFile(resolvedPath, res)
      return
    }

    // Fallback to index.html for client-side routing or missing assets
    serveFile(INDEX_FILE, res, err ? 200 : 404)
  })
})

server.listen(DEFAULT_PORT, HOST, () => {
  console.log(`CasinoSimulation client available at http://${HOST}:${DEFAULT_PORT}`)
  console.log('Press Ctrl+C to stop the server.')
})
