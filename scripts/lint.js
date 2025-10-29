#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

const ROOT = path.join(__dirname, '..')
const ALLOWED_EXTS = new Set(['.js', '.json', '.css', '.md'])
const IGNORED_DIRS = new Set(['node_modules', '.git'])

const errors = []

const walk = (dir) => {
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    if (IGNORED_DIRS.has(entry.name)) continue
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walk(fullPath)
    } else {
      const ext = path.extname(entry.name)
      if (!ALLOWED_EXTS.has(ext)) continue
      checkFile(fullPath, ext)
    }
  }
}

const checkFile = (filePath, ext) => {
  const contents = fs.readFileSync(filePath, 'utf8')
  const lines = contents.split(/\r?\n/)

  lines.forEach((line, idx) => {
    if (/\s+$/.test(line)) {
      errors.push(`${filePath}: Trailing whitespace on line ${idx + 1}`)
    }
  })

  if (!contents.endsWith('\n')) {
    errors.push(`${filePath}: File must end with a newline`)
  }

  if (ext === '.json') {
    try {
      JSON.parse(contents)
    } catch (error) {
      errors.push(`${filePath}: Invalid JSON (${error.message})`)
    }
  }
}

walk(ROOT)

if (errors.length > 0) {
  console.error('Lint issues found:')
  for (const message of errors) {
    console.error(` - ${message}`)
  }
  process.exit(1)
}

console.log('Lint checks passed.')
