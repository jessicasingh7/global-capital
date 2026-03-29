// Scale comparison bar — shows all asset classes to scale

function renderScaleBar(scaleTotals) {
  const segments = document.getElementById('scale-segments');
  const labels = document.getElementById('scale-labels');
  const totalEl = document.getElementById('scale-total');

  const classes = scaleTotals.asset_classes;
  const grandTotal = classes.reduce((s, c) => s + c.total_usd, 0);

  totalEl.textContent = '$' + formatNum(grandTotal);

  segments.innerHTML = classes.map(c => {
    const pct = (c.total_usd / grandTotal) * 100;
    if (pct < 0.5) return '';
    return `
      <div class="scale-segment"
           style="width:${pct}%;background:${c.color}"
           title="${c.name}: $${formatNum(c.total_usd)} (${pct.toFixed(1)}%)">
      </div>
    `;
  }).join('');

  labels.innerHTML = classes.map(c => {
    const pct = (c.total_usd / grandTotal) * 100;
    if (pct < 3) return `<div style="width:${pct}%"></div>`;
    return `
      <div style="width:${pct}%" class="text-[9px] text-white/40 truncate px-0.5">
        ${c.name}
      </div>
    `;
  }).join('');
}
