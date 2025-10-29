const http = require('http')
const { URL } = require('url')
const events = require('../data/events')
const promotions = require('../data/promotions')
const { simulateBets } = require('./simulator')

const PORT = process.env.PORT || 4000

const sendJson = (res, statusCode, payload) => {
  const body = JSON.stringify(payload)
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  })
  res.end(body)
}

const parseBody = (req) => new Promise((resolve, reject) => {
  let raw = ''

  req.on('data', (chunk) => {
    raw += chunk
    if (raw.length > 1e6) {
      req.destroy()
      reject(new Error('Payload too large'))
    }
  })

  req.on('end', () => {
    if (!raw) {
      resolve({})
      return
    }

    try {
      resolve(JSON.parse(raw))
    } catch (error) {
      reject(new Error('Invalid JSON body'))
    }
  })

  req.on('error', reject)
})

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`)

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    })
    res.end()
    return
  }

  if (req.method === 'GET' && url.pathname === '/api/health') {
    sendJson(res, 200, { status: 'ok' })
    return
  }

  if (req.method === 'GET' && url.pathname === '/api/events') {
    sendJson(res, 200, { events })
    return
  }

  if (req.method === 'GET' && url.pathname === '/api/promotions') {
    sendJson(res, 200, { promotions })
    return
  }

  if (req.method === 'POST' && url.pathname === '/api/simulate') {
    try {
      const body = await parseBody(req)
      const result = simulateBets(body)
      sendJson(res, 200, result)
    } catch (error) {
      sendJson(res, 400, { error: error.message })
    }
    return
  }

  sendJson(res, 404, { error: 'Not found' })
})

if (require.main === module) {
  server.listen(PORT, () => {
    // eslint-disable-next-line no-console
    console.log(`CasinoSimulation API running on port ${PORT}`)
  })
}

module.exports = { server }
