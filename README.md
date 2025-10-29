# CasinoSimulation

CasinoSimulation is a sandbox sportsbook experience built with Node.js and React (served from CDN modules).
It provides a safe way to experiment with moneyline wagers, stack parlays, and explore how common sportsbook
promotions can change your returns without wagering real money.

## Project structure

```
.
├── server          # Node HTTP API serving events, promotions, and simulation logic
└── client          # React front-end delivered as native ES modules
```

## Getting started

The repository has no third-party npm dependencies, so there is nothing to install before running the tools.

```bash
# Start the API server (http://localhost:4000)
npm --prefix server run start

# Open the client (served statically)
# Use any HTTP server to host the client directory, for example:
python3 -m http.server --directory client 5173
```

The client imports React and ReactDOM from esm.sh at runtime and calls the API on `http://localhost:4000` by default.
Override the endpoint by setting `window.CASINO_API_BASE` before loading `main.js` if you host the services elsewhere.

## Available scripts

```bash
# Run automated tests (simulation engine + client smoke test)
npm test

# Run repository lint checks
npm run lint
```

## Simulation overview

The backend exposes three routes:

- `GET /api/events` – curated list of sample moneyline markets with American and decimal odds.
- `GET /api/promotions` – sportsbook-style bonuses such as risk-free bets and parlay boosts.
- `POST /api/simulate` – runs the simulation engine on the submitted bet slip, returning detailed outcomes
  and any promo adjustments.

Use the front-end dashboard to assemble bets, choose a promotion, and execute a virtual run before placing
real wagers.
