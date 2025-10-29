const COIN_FLIP_ODDS = {
  american: -110,
  decimal: 1.91,
  probability: 0.5
}

module.exports = [
  {
    id: 'coin-flip-arena',
    league: 'Simulated League',
    name: 'Coin Flip Arena Finals',
    startTime: '2024-03-21T23:30:00Z',
    marketType: 'moneyline',
    odds: {
      home: {
        label: 'Side A',
        ...COIN_FLIP_ODDS
      },
      away: {
        label: 'Side B',
        ...COIN_FLIP_ODDS
      }
    }
  },
  {
    id: 'coin-flip-collegiate',
    league: 'Campus Classic',
    name: 'Campus Classic Coin Flip',
    startTime: '2024-03-22T17:00:00Z',
    marketType: 'moneyline',
    odds: {
      home: {
        label: 'Heads Squad',
        ...COIN_FLIP_ODDS
      },
      away: {
        label: 'Tails Crew',
        ...COIN_FLIP_ODDS
      }
    }
  },
  {
    id: 'coin-flip-showdown',
    league: 'Prime Time Sim',
    name: 'Prime Time Coin Flip Showdown',
    startTime: '2024-03-22T23:05:00Z',
    marketType: 'moneyline',
    odds: {
      home: {
        label: 'Blue Chips',
        ...COIN_FLIP_ODDS
      },
      away: {
        label: 'Red Rockets',
        ...COIN_FLIP_ODDS
      }
    }
  }
]
