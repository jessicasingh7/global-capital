const LAYERS = [
  { key: 'all', label: 'All Capital', color: '#e05050' },
  { key: 'real_estate', label: 'Real Estate', color: '#4CAF50' },
  { key: 'stocks', label: 'Stock Markets', color: '#FF9800' },
  { key: 'bonds', label: 'Bonds & Debt', color: '#2196F3' },
  { key: 'pensions', label: 'Pensions', color: '#9C27B0' },
  { key: 'pe_hf', label: 'PE & Hedge Funds', color: '#F44336' },
  { key: 'sovereign_wealth', label: 'Sovereign Wealth', color: '#00BCD4' },
  { key: 'billionaires', label: 'Billionaires', color: '#FFD700' },
  { key: 'central_bank', label: 'Central Banks', color: '#8BC34A' },
  { key: 'crypto', label: 'Crypto', color: '#E91E63' },
];

document.addEventListener('DOMContentLoaded', async () => {
  initGlobe(document.getElementById('globe'));

  // Layer toggles
  const togglesEl = document.getElementById('layer-toggles');
  LAYERS.forEach(layer => {
    const btn = document.createElement('button');
    btn.className = 'layer-toggle' + (layer.key === 'all' ? ' active' : '');
    btn.innerHTML = `<span class="dot" style="background:${layer.color}"></span>${layer.label}`;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.layer-toggle').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateGlobe(window.globeRawData, layer.key);
      updateLegendColor(layer);
    });
    togglesEl.appendChild(btn);
  });

  // Load data
  try {
    const [geoRes, globeRes, scaleRes] = await Promise.all([
      fetch('/data/countries.geojson'),
      fetch('/data/globe_total.json'),
      fetch('/data/scale_totals.json'),
    ]);

    const geo = await geoRes.json();
    setGeoFeatures(geo.features);

    window.globeRawData = await globeRes.json();
    const scaleTotals = await scaleRes.json();

    updateGlobe(window.globeRawData, 'all');
    renderScaleBar(scaleTotals);

    try {
      const r = await fetch('/data/billionaires.json');
      if (r.ok) window.billionairesData = await r.json();
    } catch (e) {}

    try {
      const r = await fetch('/data/status.json');
      if (r.ok) {
        const s = await r.json();
        document.getElementById('status').textContent = 'Updated: ' + s.updated_at;
      }
    } catch (e) {}
  } catch (err) {
    console.error('Failed to load data:', err);
  }
});

function updateLegendColor(layer) {
  const el = document.querySelector('#color-legend .gradient-bar');
  if (!el) return;
  const hex = layer.color;
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  el.style.background = `linear-gradient(to right, rgba(${r},${g},${b},0.15), rgba(${r},${g},${b},0.55), rgba(${r},${g},${b},0.95))`;
}
