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
          eventId: 'coin-flip-arena',
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

test('profit boost token adds 30% to winnings and marks promo consumed', async () => {
  await withMockedRandom([0.01], () => {
    const result = simulateBets({
      promoId: 'profit-boost-30-token',
      bets: [
        {
          eventId: 'coin-flip-arena',
          selection: 'home',
          stake: 50
        }
      ]
    })

    assert.equal(result.promoApplied.id, 'profit-boost-30-token')
    assert.equal(result.promoConsumed, true)
    assert.equal(result.bets[0].outcome, 'win')
    assert.equal(result.bets[0].promo.value, 13.65)
    assert.equal(result.netProfit, 59.15)
  })
})

test('coin flip markets resolve near 50-50 probability', async () => {
  await withMockedRandom([0.49, 0.51], () => {
    const result = simulateBets({
      bets: [
        { eventId: 'coin-flip-arena', selection: 'home', stake: 10 },
        { eventId: 'coin-flip-collegiate', selection: 'away', stake: 10 }
      ]
    })

    assert.equal(result.bets[0].outcome, 'win')
    assert.equal(result.bets[1].outcome, 'lose')
  })
})
