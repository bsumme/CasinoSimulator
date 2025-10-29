import React from 'https://esm.sh/react@18.2.0'

const h = React.createElement

const PromotionList = ({ promotions, selectedPromo, onSelectPromo }) =>
  h(
    'div',
    { className: 'promotions-list' },
    ...(promotions || []).map((promo) =>
      h(
        'label',
        { key: promo.id || 'none', className: 'promo-card' },
        h('input', {
          type: 'radio',
          name: 'promotion',
          value: promo.id,
          checked: selectedPromo === promo.id,
          onChange: () => onSelectPromo(promo.id || '')
        }),
        h(
          'div',
          { style: { marginTop: '0.5rem' } },
          h('strong', null, promo.name),
          promo.description
            ? h('p', { style: { margin: '0.35rem 0 0' } }, promo.description)
            : null
        )
      )
    )
  )

export default PromotionList
