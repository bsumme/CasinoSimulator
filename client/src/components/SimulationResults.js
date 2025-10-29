import React from 'https://esm.sh/react@18.2.0'

const h = React.createElement
const formatUSD = (value) => `$${Number(value || 0).toFixed(2)}`

const SimulationResults = ({ simulation }) => {
  if (!simulation) {
    return h('div', { className: 'empty-state' }, 'Run a simulation to see projected outcomes.')
  }

  return h(
    'div',
    { className: 'results-panel' },
    simulation.promoApplied
      ? h(
          'div',
          { className: 'promo-banner' },
          'Promotion Applied: ',
          simulation.promoApplied.name,
          h('br'),
          h('small', null, simulation.promoApplied.description)
        )
      : null,
    ...simulation.bets.map((bet) =>
      h(
        'article',
        { key: bet.eventId + bet.selectionKey, className: 'bet-result' },
        h('h3', null, bet.eventName),
        h('p', null, `${bet.selection} — Stake ${formatUSD(bet.stake)} @ decimal ${bet.decimalOdds}`),
        h('p', null, `Implied probability: ${(bet.impliedProbability * 100).toFixed(1)}%`),
        h('p', null, ['Outcome simulated: ', h('strong', { key: 'result' }, bet.outcome.toUpperCase())]),
        h(
          'p',
          null,
          `Potential payout: ${formatUSD(bet.potentialPayout)} | Net result: ${formatUSD(bet.netResult)}`
        ),
        bet.promo
          ? h('p', null, `Promo credit: ${formatUSD(bet.promo.value)} — ${bet.promo.note}`)
          : null
      )
    ),
    h(
      'div',
      { className: 'summary-card' },
      h(
        'div',
        null,
        h('span', null, 'Total Stake'),
        h('strong', null, formatUSD(simulation.totalStake))
      ),
      h(
        'div',
        null,
        h('span', null, 'Total Return'),
        h('strong', null, formatUSD(simulation.totalReturn))
      ),
      h(
        'div',
        null,
        h('span', null, 'Net Profit'),
        h('strong', null, formatUSD(simulation.netProfit))
      ),
      simulation.promo
        ? h(
            'div',
            null,
            h('span', null, 'Promo Boost'),
            h('strong', null, formatUSD(simulation.promo.value))
          )
        : null
    )
  )
}

export default SimulationResults
