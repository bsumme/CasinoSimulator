const toImpliedProbability = (decimalOdds) => {
  if (!decimalOdds || decimalOdds <= 1) {
    return 0
  }
  return 1 / decimalOdds
}

const formatCurrency = (amount) => Number(amount.toFixed(2))

module.exports = { toImpliedProbability, formatCurrency }
