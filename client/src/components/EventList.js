import React from 'https://esm.sh/react@18.2.0'

const h = React.createElement

const formatStartTime = (startTime) => {
  const date = new Date(startTime)
  return date.toLocaleString(undefined, {
    weekday: 'short',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const formatOdds = (value) => (value > 0 ? `+${value}` : value)

const EventList = ({ events, onAddBet }) => {
  if (!events || events.length === 0) {
    return h('div', { className: 'empty-state' }, 'Events are loading…')
  }

  return h(
    'div',
    { className: 'events-list' },
    ...events.map((event) =>
      h(
        'article',
        { key: event.id, className: 'event-card' },
        h('h3', null, event.name),
        h('p', null, `${event.league} • ${formatStartTime(event.startTime)}`),
        h(
          'div',
          { className: 'moneyline' },
          h(
            'button',
            {
              type: 'button',
              onClick: () =>
                onAddBet({
                  eventId: event.id,
                  selection: 'home',
                  label: event.odds.home.label,
                  odds: event.odds.home.american
                })
            },
            h(React.Fragment, null,
              h('span', null, event.odds.home.label),
              h('br'),
              h('span', null, formatOdds(event.odds.home.american))
            )
          ),
          h(
            'button',
            {
              type: 'button',
              onClick: () =>
                onAddBet({
                  eventId: event.id,
                  selection: 'away',
                  label: event.odds.away.label,
                  odds: event.odds.away.american
                })
            },
            h(React.Fragment, null,
              h('span', null, event.odds.away.label),
              h('br'),
              h('span', null, formatOdds(event.odds.away.american))
            )
          )
        )
      )
    )
  )
}

export default EventList
