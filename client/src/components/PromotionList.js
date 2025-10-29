import React from 'https://esm.sh/react@18.2.0'

const h = React.createElement

const PromotionList = ({ promotions, selectedPromo, onSelectPromo, tokensLeft = 0 }) =>
  h(
    'div',
    { className: 'promotions-list' },
    ...(promotions || []).map((promo) => {
      const isNoPromo = !promo.id
      const isDisabled = !isNoPromo && tokensLeft <= 0
      const tokenMessage = isNoPromo
        ? null
        : tokensLeft > 0
          ? `${tokensLeft} token${tokensLeft === 1 ? '' : 's'} remaining`
          : 'No tokens available'

      return h(
        'label',
        {
          key: promo.id || 'none',
          className: `promo-card${isDisabled ? ' promo-card--disabled' : ''}`
        },
        h('input', {
          type: 'radio',
          name: 'promotion',
          value: promo.id,
          checked: selectedPromo === promo.id,
          onChange: () => onSelectPromo(promo.id || ''),
          disabled: isDisabled
        }),
        h(
          'div',
          { style: { marginTop: '0.5rem' } },
          h('strong', null, promo.name),
          promo.description
            ? h('p', { style: { margin: '0.35rem 0 0' } }, promo.description)
            : null,
          tokenMessage
            ? h('p', { className: 'promo-meta' }, tokenMessage)
            : null
        )
      )
    })
  )

export default PromotionList
