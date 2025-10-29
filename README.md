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

### Prerequisites

- Node.js 18 or newer (ships with a compatible version of `npm`).
- Python 3 (only required if you use the built-in `http.server` helper to serve the front end).

No additional dependencies need to be installed – both the API and the client rely solely on standard library tooling.

### Step-by-step local setup

1. **Start the API server** (listens on <http://localhost:4000>):

   ```bash
   npm --prefix server run start
   ```

   Leave this process running. It exposes the REST endpoints that power the simulation.

2. **Serve the client application** from another terminal window. Any static file host will work; the example below uses Python's built-in server on port `5173`:

   ```bash
   python3 -m http.server --directory client 5173
   ```

3. **Open the dashboard** by navigating to <http://localhost:5173> in your browser. The React application will automatically fetch data from the API server you started in step 1.

The client imports React and ReactDOM from esm.sh at runtime and calls the API on `http://localhost:4000` by default.
If you need to target a different backend, define `window.CASINO_API_BASE = "http://your-host:port";` in `index.html`
before `main.js` is loaded.

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
