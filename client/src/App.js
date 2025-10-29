import React, { useEffect, useMemo, useState } from 'https://esm.sh/react@18.2.0'
import EventList from './components/EventList.js'
import PromotionList from './components/PromotionList.js'
import BetSlip from './components/BetSlip.js'
import SimulationResults from './components/SimulationResults.js'

const h = React.createElement

const API_BASE_URL = (typeof window !== 'undefined' && window.CASINO_API_BASE) || 'http://localhost:4000'

const formatUSD = (value) => `$${Number(value || 0).toFixed(2)}`

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
  const [account, setAccount] = useState({ balance: 500, boostTokens: 3 })

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

  const totalStake = useMemo(
    () =>
      bets.reduce((sum, bet) => {
        const stakeValue = Number(bet.stake)
        return Number.isNaN(stakeValue) ? sum : sum + stakeValue
      }, 0),
    [bets]
  )

  const handleAddBet = (bet) => {
    const defaultStake = Number.isFinite(Number(bet.stake)) ? Number(bet.stake) : 10
    setBets((prev) => [...prev, { ...bet, stake: defaultStake }])
  }

  const handleRemoveBet = (index) => {
    setBets((prev) => prev.filter((_, idx) => idx !== index))
  }

  const handleUpdateStake = (index, stake) => {
    const sanitizedStake = Number.isNaN(Number(stake)) ? 0 : Number(stake)
    setBets((prev) => prev.map((bet, idx) => (idx === index ? { ...bet, stake: sanitizedStake } : bet)))
  }

  const handleSimulate = async () => {
    if (bets.length === 0) {
      setError('Add at least one bet to simulate your slip.')
      return
    }

    const hasInvalidStake = bets.some((bet) => Number(bet.stake) <= 0)
    if (hasInvalidStake) {
      setError('Each wager must have a stake of at least $1.00.')
      return
    }

    if (totalStake > account.balance) {
      setError(`Insufficient balance. You need ${formatUSD(totalStake)} but only have ${formatUSD(account.balance)}.`)
      return
    }

    if (selectedPromo && account.boostTokens === 0) {
      setError('You have no profit boost tokens remaining.')
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
      setAccount((prev) => {
        const updatedBalance = Number((prev.balance + Number(data.netProfit || 0)).toFixed(2))
        const shouldConsumeToken = Boolean(data.promoConsumed && selectedPromo && prev.boostTokens > 0)
        return {
          balance: updatedBalance,
          boostTokens: shouldConsumeToken ? prev.boostTokens - 1 : prev.boostTokens
        }
      })
      setBets([])
      if (selectedPromo) {
        setSelectedPromo('')
      }
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
      ),
      h(
        'div',
        { className: 'account-summary' },
        h('span', null, `Account Balance: ${formatUSD(account.balance)}`),
        h('span', null, `Profit Boost Tokens: ${account.boostTokens}`)
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
          onSelectPromo: setSelectedPromo,
          tokensLeft: account.boostTokens
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
          isLoading,
          balance: account.balance,
          totalStake,
          hasInsufficientFunds: totalStake > account.balance
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
