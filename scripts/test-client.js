#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

const appPath = path.join(__dirname, '..', 'client', 'src', 'App.js')
const appContents = fs.readFileSync(appPath, 'utf8')

if (!appContents.includes('CasinoSimulation Sportsbook Lab')) {
  console.error('App.js is missing the primary headline.')
  process.exit(1)
}

if (!appContents.includes('Simulation Results')) {
  console.error('App.js is missing the simulation results header.')
  process.exit(1)
}

console.log('Client smoke test passed.')
