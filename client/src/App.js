import React, { useEffect, useMemo, useState } from 'https://esm.sh/react@18.2.0'
import EventList from './components/EventList.js'
import PromotionList from './components/PromotionList.js'
import BetSlip from './components/BetSlip.js'
import SimulationResults from './components/SimulationResults.js'

const h = React.createElement

const API_BASE_URL = (typeof window !== 'undefined' && window.CASINO_API_BASE) || 'http://localhost:4000'

const fetchJson = async (path) => {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error('Network response was not ok')
  }
  return response.json()
}

const App = () => {
  const [events, setEvents] = useState([])
  const [promotions, setPromotions] = useState([])
  const [bets, setBets] = useState([])
  const [selectedPromo, setSelectedPromo] = useState('')
  const [simulation, setSimulation] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([fetchJson('/api/events'), fetchJson('/api/promotions')])
      .then(([eventsPayload, promosPayload]) => {
        setEvents(eventsPayload.events || [])
        setPromotions(promosPayload.promotions || [])
      })
      .catch(() => {
        setError('Unable to load events right now. Please try again later.')
      })
  }, [])

  const promoOptions = useMemo(
    () => [{ id: '', name: 'No Promotion' }, ...promotions],
    [promotions]
  )

  const handleAddBet = (bet) => {
    setBets((prev) => [...prev, { ...bet, stake: bet.stake ?? 10 }])
  }

  const handleRemoveBet = (index) => {
    setBets((prev) => prev.filter((_, idx) => idx !== index))
  }

  const handleUpdateStake = (index, stake) => {
    setBets((prev) => prev.map((bet, idx) => (idx === index ? { ...bet, stake } : bet)))
  }

  const handleSimulate = async () => {
    if (bets.length === 0) {
      setError('Add at least one bet to simulate your slip.')
      return
    }

    setIsLoading(true)
    setError('')
    setSimulation(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          promoId: selectedPromo || undefined,
          bets: bets.map((bet) => ({
            eventId: bet.eventId,
            selection: bet.selection,
            stake: Number(bet.stake)
          }))
        })
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}))
        throw new Error(payload.error || 'Simulation failed')
      }

      const data = await response.json()
      setSimulation(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return h(
    'div',
    { className: 'app-shell' },
    h(
      'header',
      null,
      h('h1', null, 'CasinoSimulation Sportsbook Lab'),
      h(
        'p',
        null,
        'Experiment with moneyline wagers, stack parlays, and explore promotional boosts without risking real money. This sandbox mirrors a modern sportsbook experience while giving you insights into how promos impact your expected returns.'
      )
    ),
    error
      ? h(
          'div',
          { className: 'promo-banner', role: 'alert' },
          error
        )
      : null,
    h(
      'div',
      { className: 'dashboard' },
      h(
        'section',
        { className: 'panel' },
        h('h2', null, 'Live Events'),
        h(EventList, { events, onAddBet: handleAddBet })
      ),
      h(
        'section',
        { className: 'panel' },
        h('h2', null, 'Promotions'),
        h(PromotionList, {
          promotions: promoOptions,
          selectedPromo,
          onSelectPromo: setSelectedPromo
        })
      ),
      h(
        'section',
        { className: 'panel' },
        h('h2', null, 'Bet Slip'),
        h(BetSlip, {
          bets,
          events,
          onRemoveBet: handleRemoveBet,
          onUpdateStake: handleUpdateStake,
          onSimulate: handleSimulate,
          isLoading
        })
      )
    ),
    h(
      'section',
      { className: 'panel', style: { marginTop: '1.5rem' } },
      h('h2', null, 'Simulation Results'),
      h(SimulationResults, { simulation })
    )
  )
}

export default App
