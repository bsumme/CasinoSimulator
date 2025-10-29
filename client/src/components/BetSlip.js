import React from 'https://esm.sh/react@18.2.0'

const h = React.createElement

const findEventName = (events, eventId) => {
  const event = (events || []).find((item) => item.id === eventId)
  return event ? event.name : 'Unknown event'
}

const BetSlip = ({ bets, events, onRemoveBet, onUpdateStake, onSimulate, isLoading }) =>
  h(
    'div',
    { className: 'bet-slip' },
    (!bets || bets.length === 0)
      ? h('div', { className: 'empty-state' }, 'Select a side to start building your slip.')
      : null,
    ...((bets || []).map((bet, index) =>
      h(
        'div',
        { key: `${bet.eventId}-${bet.selection}-${index}`, className: 'bet-card' },
        h(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' } },
          h(
            'div',
            null,
            h('strong', null, findEventName(events, bet.eventId)),
            h(
              'div',
              { className: 'selection-tag' },
              `${bet.label} • ${bet.odds > 0 ? `+${bet.odds}` : bet.odds}`
            )
          ),
          h(
            'button',
            {
              type: 'button',
              onClick: () => onRemoveBet(index),
              'aria-label': `Remove ${bet.label} from slip`,
              style: {
                border: 'none',
                background: 'transparent',
                color: '#f87171',
                cursor: 'pointer',
                fontWeight: 600
              }
            },
            'Remove'
          )
        ),
        h(
          'label',
          { style: { display: 'block', marginTop: '0.75rem' } },
          'Stake ($)',
          h('input', {
            type: 'number',
            min: '1',
            value: bet.stake,
            onChange: (event) => onUpdateStake(index, Number(event.target.value))
          })
        )
      )
    )),
    h(
      'button',
      { type: 'button', onClick: onSimulate, disabled: isLoading },
      isLoading ? 'Simulating…' : 'Run Simulation'
    )
  )

export default BetSlip
