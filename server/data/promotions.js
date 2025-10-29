module.exports = [
  {
    id: 'risk-free-50',
    name: 'Risk-Free Bet up to $50',
    description: 'Get your stake back as a free bet if your first wager loses (max $50).',
    type: 'insurance',
    limit: 50
  },
  {
    id: 'profit-boost-20',
    name: '20% Profit Boost',
    description: 'Increase net winnings by 20% on any single bet.',
    type: 'profitBoost',
    boost: 0.2
  },
  {
    id: 'parlay-power-30',
    name: 'Parlay Power 30%',
    description: 'Get a 30% boost on parlays with 3+ legs.',
    type: 'parlayBoost',
    boost: 0.3,
    minLegs: 3
  }
]
