const events = require('../data/events')
const promotions = require('../data/promotions')
const { toImpliedProbability, formatCurrency } = require('./utils')

const getEventById = (eventId) => events.find((event) => event.id === eventId)

const getPromoById = (promoId) => promotions.find((promo) => promo.id === promoId)

const applyInsurance = (betResult, promo) => {
  if (betResult.outcome === 'lose') {
    const credit = Math.min(betResult.stake, promo.limit)
    betResult.promo = {
      id: promo.id,
      description: promo.description,
      value: formatCurrency(credit),
      note: 'Credit issued for lost wager'
    }
    betResult.netResult += credit
  }
}

const applyProfitBoost = (betResult, promo) => {
  if (betResult.outcome === 'win') {
    const boostValue = betResult.netResult * promo.boost
    betResult.netResult += boostValue
    betResult.promo = {
      id: promo.id,
      description: promo.description,
      value: formatCurrency(boostValue),
      note: 'Boost applied to winnings'
    }
  }
}

const applyParlayBoost = (summary, promo) => {
  const { bets } = summary
  if (bets.length < promo.minLegs) {
    return
  }

  const winningBets = bets.filter((bet) => bet.outcome === 'win')
  if (winningBets.length === bets.length) {
    const boostValue = summary.netProfit * promo.boost
    summary.netProfit += boostValue
    summary.promo = {
      id: promo.id,
      description: promo.description,
      value: formatCurrency(boostValue),
      note: 'Parlay boost applied to all-leg win'
    }
  }
}

const simulateBets = ({ bets, promoId }) => {
  if (!Array.isArray(bets) || bets.length === 0) {
    throw new Error('At least one bet is required for simulation')
  }

  const promo = promoId ? getPromoById(promoId) : undefined

  let promoConsumed = false

  const betResults = bets.map((bet) => {
    const event = getEventById(bet.eventId)
    if (!event) {
      throw new Error(`Unknown event: ${bet.eventId}`)
    }

    const selection = event.odds[bet.selection]
    if (!selection) {
      throw new Error(`Invalid selection for event ${event.id}`)
    }

    const stake = Number(bet.stake)
    if (Number.isNaN(stake) || stake <= 0) {
      throw new Error('Stake must be a positive number')
    }

    const impliedProbability = selection.probability ?? toImpliedProbability(selection.decimal)
    const potentialPayout = stake * selection.decimal
    const outcome = Math.random() <= impliedProbability ? 'win' : 'lose'
    const netResult = outcome === 'win' ? potentialPayout - stake : -stake

    return {
      eventId: event.id,
      eventName: event.name,
      selection: selection.label,
      selectionKey: bet.selection,
      stake: formatCurrency(stake),
      decimalOdds: selection.decimal,
      americanOdds: selection.american,
      impliedProbability: Number(impliedProbability.toFixed(3)),
      potentialPayout: formatCurrency(potentialPayout),
      outcome,
      netResult
    }
  })

  const summary = {
    bets: betResults,
    totalStake: formatCurrency(betResults.reduce((sum, bet) => sum + bet.stake, 0)),
    totalReturn: 0,
    netProfit: 0
  }

  betResults.forEach((bet) => {
    if (promo && promo.type === 'insurance' && !summary.promo) {
      applyInsurance(bet, promo)
      promoConsumed = true
    } else if (promo && promo.type === 'profitBoost' && !promoConsumed) {
      promoConsumed = true
      applyProfitBoost(bet, promo)
    }

    summary.totalReturn += bet.outcome === 'win' ? bet.stake + (bet.netResult > 0 ? bet.netResult : 0) : 0
    summary.netProfit += bet.netResult
  })

  summary.totalReturn = formatCurrency(summary.totalReturn)
  summary.netProfit = formatCurrency(summary.netProfit)

  if (promo && promo.type === 'parlayBoost') {
    applyParlayBoost(summary, promo)
    if (summary.promo) {
      promoConsumed = true
      summary.promo.value = formatCurrency(summary.promo.value)
      summary.netProfit = formatCurrency(summary.netProfit)
    }
  }

  return {
    promoApplied: promo ? {
      id: promo.id,
      name: promo.name,
      description: promo.description
    } : null,
    promoConsumed,
    ...summary
  }
}

module.exports = { simulateBets, getEventById, getPromoById }
