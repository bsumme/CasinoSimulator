const test = require('node:test')
const assert = require('node:assert/strict')
const { simulateBets } = require('../simulator')

const withMockedRandom = async (values, callback) => {
  const originalRandom = Math.random
  let index = 0
  Math.random = () => {
    const value = values[index % values.length]
    index += 1
    return value
  }

  try {
    await callback()
  } finally {
    Math.random = originalRandom
  }
}

test('simulateBets throws when no bets are provided', () => {
  assert.throws(() => simulateBets({ bets: [] }), /At least one bet is required/)
})

test('simulateBets returns a winning bet without promos', async () => {
  await withMockedRandom([0.2], () => {
    const result = simulateBets({
      bets: [
        {
          eventId: 'nba-lal-bos',
          selection: 'home',
          stake: 25
        }
      ]
    })

    assert.equal(result.bets.length, 1)
    assert.equal(result.bets[0].outcome, 'win')
    assert.ok(result.netProfit > 0)
  })
})

test('risk-free promo credits stake on a loss', async () => {
  await withMockedRandom([0.99], () => {
    const result = simulateBets({
      promoId: 'risk-free-50',
      bets: [
        {
          eventId: 'nba-lal-bos',
          selection: 'home',
          stake: 40
        }
      ]
    })

    assert.equal(result.bets[0].outcome, 'lose')
    assert.equal(result.bets[0].promo.value, 40)
    assert.equal(result.netProfit, 0)
  })
})

test('parlay boost requires all legs to win', async () => {
  await withMockedRandom([0.99, 0.99, 0.99], () => {
    const result = simulateBets({
      promoId: 'parlay-power-30',
      bets: [
        { eventId: 'nba-lal-bos', selection: 'home', stake: 10 },
        { eventId: 'nfl-kc-buf', selection: 'home', stake: 10 },
        { eventId: 'mlb-nyy-lad', selection: 'home', stake: 10 }
      ]
    })

    assert.equal(result.promo, undefined)
    assert.ok(result.netProfit < 0)
  })
})
