const ASSET_COLORS = {
  real_estate: '#4CAF50',
  stocks: '#FF9800',
  bonds: '#2196F3',
  pensions: '#9C27B0',
  pe_hf: '#F44336',
  sovereign_wealth: '#00BCD4',
  billionaires: '#FFD700',
  central_bank: '#8BC34A',
  bigtech: '#E040FB',
  vc: '#FF5722',
  crypto: '#E91E63',
  insurance: '#607D8B',
  remittances: '#FFAB40',
  foreign_aid: '#69F0AE',
};

let myGlobe;
let geoFeatures = [];
let globeData = [];
let countryLookup = {};

function initGlobe(container) {
  myGlobe = Globe()(container)
    .backgroundColor('#1a1a2e')
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .showAtmosphere(true)
    .atmosphereColor('#4466aa')
    .atmosphereAltitude(0.15)
    .polygonGeoJsonGeometry(d => d.geometry)
    .polygonCapColor(d => d._color)
    .polygonSideColor(() => 'rgba(0,0,0,0.3)')
    .polygonAltitude(d => d._alt)
    .polygonLabel(d => d._label)
    .onPolygonClick(d => {
      if (d._code && countryLookup[d._code]) showPanel(d._code);
    })
    .polygonsTransitionDuration(300)
    .width(container.clientWidth || window.innerWidth)
    .height(container.clientHeight || (window.innerHeight - 120));

  myGlobe.controls().autoRotate = true;
  myGlobe.controls().autoRotateSpeed = 0.4;
  myGlobe.controls().enableDamping = true;

  window.addEventListener('resize', () => {
    myGlobe.width(container.clientWidth || window.innerWidth)
           .height(container.clientHeight || (window.innerHeight - 120));
  });
}

function setGeoFeatures(features) {
  geoFeatures = features.filter(d => d.geometry);
}

function updateGlobe(data, layer) {
  globeData = data;
  layer = layer || 'all';

  countryLookup = {};
  data.forEach(c => { countryLookup[c.country_code] = c; });

  let maxVal = 0;
  data.forEach(c => {
    const val = layer === 'all' ? c.total_capital_usd : (c.breakdown[layer] || 0);
    if (val > maxVal) maxVal = val;
  });

  const polygons = geoFeatures.map(f => {
    const code = f.properties.ISO_A3;
    const name = f.properties.NAME || code;
    const country = countryLookup[code];
    const val = country
      ? (layer === 'all' ? country.total_capital_usd : (country.breakdown[layer] || 0))
      : 0;
    const t = maxVal > 0 && val > 0 ? Math.pow(val / maxVal, 0.35) : 0;

    let color;
    if (!val) {
      color = '#222240';
    } else if (layer === 'all') {
      color = `rgb(255, ${Math.round(180 - t * 130)}, ${Math.round(120 - t * 40)})`;
    } else {
      const base = ASSET_COLORS[layer] || '#FF9800';
      const br = parseInt(base.slice(1,3), 16);
      const bg = parseInt(base.slice(3,5), 16);
      const bb = parseInt(base.slice(5,7), 16);
      color = `rgb(${Math.round(40 + (br-40)*t)}, ${Math.round(40 + (bg-40)*t)}, ${Math.round(60 + (bb-60)*t)})`;
    }

    const alt = val ? 0.01 + t * 0.06 : 0.005;

    return {
      ...f,
      _code: code,
      _color: color,
      _alt: alt,
      _label: `<div style="background:rgba(15,15,30,0.95);padding:10px 14px;border-radius:8px;font-size:13px;color:white;border:1px solid rgba(255,255,255,0.15);min-width:150px">
        <div style="font-weight:700;margin-bottom:3px">${name}</div>
        <div style="color:#ff8866;font-family:monospace;font-size:16px;font-weight:700">${val ? '$' + formatNum(val) : 'No data'}</div>
        ${country ? '<div style="color:rgba(255,255,255,0.3);font-size:10px;margin-top:4px">Click for breakdown</div>' : ''}
      </div>`,
    };
  });

  myGlobe.polygonsData(polygons);
}

function formatNum(n) {
  if (n >= 1e12) return (n / 1e12).toFixed(1) + 'T';
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  return n.toLocaleString();
}
