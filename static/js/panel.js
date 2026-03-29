function showPanel(countryCode) {
  const country = globeData.find(c => c.country_code === countryCode);
  if (!country) return;

  document.getElementById('panel').classList.remove('hidden');
  document.getElementById('panel-title').textContent = country.country_name;
  const total = document.getElementById('panel-total');
  total.textContent = '$' + formatNum(country.total_capital_usd);
  total.style.color = '#ff8866';

  myGlobe.controls().autoRotate = false;

  const entries = Object.entries(country.breakdown)
    .filter(([, v]) => v > 0)
    .sort((a, b) => b[1] - a[1]);
  const maxVal = entries.length > 0 ? entries[0][1] : 1;

  document.getElementById('panel-breakdown').innerHTML = entries.map(([key, val]) => {
    const pct = (val / maxVal) * 100;
    const color = ASSET_COLORS[key] || '#666';
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    return `<div class="breakdown-row">
      <div class="w-24 text-xs text-white/50 shrink-0">${label}</div>
      <div class="flex-1"><div class="breakdown-bar" style="width:${pct}%;background:${color}"></div></div>
      <div class="text-xs text-white/70 font-mono w-16 text-right">$${formatNum(val)}</div>
    </div>`;
  }).join('');

  const billSection = document.getElementById('panel-billionaires');
  if (window.billionairesData) {
    const list = window.billionairesData
      .filter(b => b.country_code === countryCode)
      .sort((a, b) => b.net_worth_usd - a.net_worth_usd)
      .slice(0, 10);
    billSection.innerHTML = list.length ? `
      <h3 class="text-xs text-white/40 uppercase tracking-wider mb-2">Top Billionaires</h3>
      ${list.map(b => `<div class="flex items-center justify-between py-1.5 border-b border-white/5">
        <div><div class="text-sm">${b.name}</div><div class="text-xs text-white/40">${b.source || b.industry}</div></div>
        <div class="text-sm font-mono text-orange-400">$${formatNum(b.net_worth_usd)}</div>
      </div>`).join('')}` : '';
  }
}

function closePanel() {
  document.getElementById('panel').classList.add('hidden');
  myGlobe.controls().autoRotate = true;
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('panel-close').addEventListener('click', closePanel);
});
