"""Expand country coverage using World Bank API — covers 200+ countries."""

import json
import requests
from .config import DATA_DIR, STATIC_DATA_DIR

WB_BASE = "https://api.worldbank.org/v2"

# Country lat/lng for globe positioning
COUNTRY_COORDS = {
    "AFG":{"lat":33.94,"lng":67.71},"ALB":{"lat":41.15,"lng":20.17},"DZA":{"lat":28.03,"lng":1.66},
    "AGO":{"lat":-11.20,"lng":17.87},"ARG":{"lat":-38.42,"lng":-63.62},"ARM":{"lat":40.07,"lng":45.04},
    "AZE":{"lat":40.14,"lng":47.58},"BGD":{"lat":23.68,"lng":90.36},"BLR":{"lat":53.71,"lng":27.95},
    "BEL":{"lat":50.50,"lng":4.47},"BEN":{"lat":9.31,"lng":2.32},"BTN":{"lat":27.51,"lng":90.43},
    "BOL":{"lat":-16.29,"lng":-63.59},"BIH":{"lat":43.92,"lng":17.68},"BWA":{"lat":-22.33,"lng":24.68},
    "BRN":{"lat":4.54,"lng":114.73},"BGR":{"lat":42.73,"lng":25.49},"BFA":{"lat":12.24,"lng":-1.56},
    "BDI":{"lat":-3.37,"lng":29.92},"KHM":{"lat":12.57,"lng":104.99},"CMR":{"lat":7.37,"lng":12.35},
    "CAF":{"lat":6.61,"lng":20.94},"TCD":{"lat":15.45,"lng":18.73},"CHL":{"lat":-35.68,"lng":-71.54},
    "COL":{"lat":4.57,"lng":-74.30},"COD":{"lat":-4.04,"lng":21.76},"COG":{"lat":-0.23,"lng":15.83},
    "CRI":{"lat":9.75,"lng":-83.75},"CIV":{"lat":7.54,"lng":-5.55},"HRV":{"lat":45.10,"lng":15.20},
    "CUB":{"lat":21.52,"lng":-77.78},"CYP":{"lat":35.13,"lng":33.43},"CZE":{"lat":49.82,"lng":15.47},
    "DNK":{"lat":56.26,"lng":9.50},"DJI":{"lat":11.83,"lng":42.59},"DOM":{"lat":18.74,"lng":-70.16},
    "ECU":{"lat":-1.83,"lng":-78.18},"EGY":{"lat":26.82,"lng":30.80},"SLV":{"lat":13.79,"lng":-88.90},
    "GNQ":{"lat":1.65,"lng":10.27},"ERI":{"lat":15.18,"lng":39.78},"EST":{"lat":58.60,"lng":25.01},
    "SWZ":{"lat":-26.52,"lng":31.47},"ETH":{"lat":9.15,"lng":40.49},"FIN":{"lat":61.92,"lng":25.75},
    "GAB":{"lat":-0.80,"lng":11.61},"GMB":{"lat":13.44,"lng":-15.31},"GEO":{"lat":42.32,"lng":43.36},
    "GHA":{"lat":7.95,"lng":-1.02},"GRC":{"lat":39.07,"lng":21.82},"GTM":{"lat":15.78,"lng":-90.23},
    "GIN":{"lat":9.95,"lng":-9.70},"GNB":{"lat":11.80,"lng":-15.18},"GUY":{"lat":4.86,"lng":-58.93},
    "HTI":{"lat":18.97,"lng":-72.29},"HND":{"lat":15.20,"lng":-86.24},"HUN":{"lat":47.16,"lng":19.50},
    "ISL":{"lat":64.96,"lng":-19.02},"IRN":{"lat":32.43,"lng":53.69},"IRQ":{"lat":33.22,"lng":43.68},
    "IRL":{"lat":53.14,"lng":-7.69},"JAM":{"lat":18.11,"lng":-77.30},"JOR":{"lat":30.59,"lng":36.24},
    "KAZ":{"lat":48.02,"lng":66.92},"KEN":{"lat":-0.02,"lng":37.91},"PRK":{"lat":40.34,"lng":127.51},
    "XKX":{"lat":42.60,"lng":20.90},"KGZ":{"lat":41.20,"lng":74.77},"LAO":{"lat":19.86,"lng":102.50},
    "LVA":{"lat":56.88,"lng":24.60},"LBN":{"lat":33.85,"lng":35.86},"LSO":{"lat":-29.61,"lng":28.23},
    "LBR":{"lat":6.43,"lng":-9.43},"LBY":{"lat":26.34,"lng":17.23},"LTU":{"lat":55.17,"lng":23.88},
    "LUX":{"lat":49.82,"lng":6.13},"MDG":{"lat":-18.77,"lng":46.87},"MWI":{"lat":-13.25,"lng":34.30},
    "MYS":{"lat":4.21,"lng":101.98},"MLI":{"lat":17.57,"lng":-4.00},"MRT":{"lat":21.01,"lng":-10.94},
    "MUS":{"lat":-20.35,"lng":57.55},"MDA":{"lat":47.41,"lng":28.37},"MNG":{"lat":46.86,"lng":103.85},
    "MNE":{"lat":42.71,"lng":19.37},"MAR":{"lat":31.79,"lng":-7.09},"MOZ":{"lat":-18.67,"lng":35.53},
    "MMR":{"lat":21.91,"lng":95.96},"NAM":{"lat":-22.96,"lng":18.49},"NPL":{"lat":28.39,"lng":84.12},
    "NZL":{"lat":-40.90,"lng":174.89},"NIC":{"lat":12.87,"lng":-85.21},"NER":{"lat":17.61,"lng":8.08},
    "MKD":{"lat":41.51,"lng":21.75},"OMN":{"lat":21.51,"lng":55.92},"PAK":{"lat":30.38,"lng":69.35},
    "PAN":{"lat":8.54,"lng":-80.78},"PNG":{"lat":-6.31,"lng":143.96},"PRY":{"lat":-23.44,"lng":-58.44},
    "PER":{"lat":-9.19,"lng":-75.02},"PHL":{"lat":12.88,"lng":121.77},"POL":{"lat":51.92,"lng":19.15},
    "PRT":{"lat":39.40,"lng":-8.22},"ROU":{"lat":45.94,"lng":24.97},"RWA":{"lat":-1.94,"lng":29.87},
    "SEN":{"lat":14.50,"lng":-14.45},"SRB":{"lat":44.02,"lng":21.01},"SLE":{"lat":8.46,"lng":-11.78},
    "SVK":{"lat":48.67,"lng":19.70},"SVN":{"lat":46.15,"lng":14.99},"SOM":{"lat":5.15,"lng":46.20},
    "SSD":{"lat":6.88,"lng":31.31},"LKA":{"lat":7.87,"lng":80.77},"SDN":{"lat":12.86,"lng":30.22},
    "SUR":{"lat":3.92,"lng":-56.03},"TJK":{"lat":38.86,"lng":71.28},"TZA":{"lat":-6.37,"lng":34.89},
    "THA":{"lat":15.87,"lng":100.99},"TLS":{"lat":-8.87,"lng":125.73},"TGO":{"lat":8.62,"lng":1.21},
    "TTO":{"lat":10.69,"lng":-61.22},"TUN":{"lat":33.89,"lng":9.54},"TKM":{"lat":38.97,"lng":59.56},
    "UGA":{"lat":1.37,"lng":32.29},"UKR":{"lat":48.38,"lng":31.17},"URY":{"lat":-32.52,"lng":-55.77},
    "UZB":{"lat":41.38,"lng":64.59},"VEN":{"lat":6.42,"lng":-66.59},"VNM":{"lat":14.06,"lng":108.28},
    "YEM":{"lat":15.55,"lng":48.52},"ZMB":{"lat":-13.13,"lng":28.64},"ZWE":{"lat":-19.02,"lng":29.15},
    "TWN":{"lat":23.70,"lng":120.96},"USA":{"lat":37.09,"lng":-95.71},"CHN":{"lat":35.86,"lng":104.19},
    "JPN":{"lat":36.20,"lng":138.25},"GBR":{"lat":55.38,"lng":-3.44},"DEU":{"lat":51.17,"lng":10.45},
    "FRA":{"lat":46.23,"lng":2.21},"IND":{"lat":20.59,"lng":78.96},"CAN":{"lat":56.13,"lng":-106.35},
    "AUS":{"lat":-25.27,"lng":133.78},"KOR":{"lat":35.91,"lng":127.77},"BRA":{"lat":-14.24,"lng":-51.93},
    "ITA":{"lat":41.87,"lng":12.57},"ESP":{"lat":40.46,"lng":-3.75},"MEX":{"lat":23.63,"lng":-102.55},
    "IDN":{"lat":-0.79,"lng":113.92},"CHE":{"lat":46.82,"lng":8.23},"NLD":{"lat":52.13,"lng":5.29},
    "SAU":{"lat":23.89,"lng":45.08},"ARE":{"lat":23.42,"lng":53.85},"SGP":{"lat":1.35,"lng":103.82},
    "NOR":{"lat":60.47,"lng":8.47},"SWE":{"lat":60.13,"lng":18.64},"ISR":{"lat":31.05,"lng":34.85},
    "HKG":{"lat":22.40,"lng":114.11},"RUS":{"lat":61.52,"lng":105.32},"TUR":{"lat":38.96,"lng":35.24},
    "ZAF":{"lat":-30.56,"lng":22.94},"NGA":{"lat":9.08,"lng":8.68},"KWT":{"lat":29.31,"lng":47.48},
    "QAT":{"lat":25.35,"lng":51.18},
}


def fetch_wb_all_countries(indicator, year=2023):
    """Fetch a World Bank indicator for ALL countries."""
    url = f"{WB_BASE}/country/all/indicator/{indicator}"
    params = {
        'date': f'{year-2}:{year}',  # try recent 3 years
        'format': 'json',
        'per_page': 500,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if len(data) < 2:
        return {}

    # Get most recent value per country
    by_country = {}
    for entry in data[1]:
        if entry['value'] is None:
            continue
        code = entry['countryiso3code']
        if not code or len(code) != 3:
            continue
        year_val = int(entry['date'])
        if code not in by_country or year_val > by_country[code]['year']:
            by_country[code] = {'value': entry['value'], 'year': year_val}

    return {k: v['value'] for k, v in by_country.items()}


def expand_countries():
    """Build comprehensive country data from World Bank."""
    print("Fetching World Bank data for all countries...")

    print("  GDP...")
    gdp = fetch_wb_all_countries('NY.GDP.MKTP.CD')
    print(f"    Got {len(gdp)} countries")

    print("  Population...")
    pop = fetch_wb_all_countries('SP.POP.TOTL')
    print(f"    Got {len(pop)} countries")

    print("  Market cap % of GDP...")
    mkt_pct = fetch_wb_all_countries('CM.MKT.LCAP.GD.ZS')
    print(f"    Got {len(mkt_pct)} countries")

    print("  Central gov debt % of GDP...")
    debt_pct = fetch_wb_all_countries('GC.DOD.TOTL.GD.ZS')
    print(f"    Got {len(debt_pct)} countries")

    # Load existing data to preserve rich fields (billionaires, VC, etc.)
    existing = {}
    globe_path = DATA_DIR / 'globe_total.json'
    if globe_path.exists():
        with open(globe_path) as f:
            for c in json.load(f):
                existing[c['country_code']] = c

    # Build comprehensive dataset
    all_countries = set(gdp.keys()) | set(pop.keys())
    # Filter to actual countries (exclude aggregates like "WLD", "EUU", etc.)
    skip_codes = {'WLD', 'EUU', 'EAS', 'ECS', 'LCN', 'MEA', 'NAC', 'SAS', 'SSF',
                  'SSA', 'OED', 'LDC', 'HPC', 'EMU', 'EAP', 'LAC', 'MNA', 'ECA',
                  'ARB', 'CEB', 'CSS', 'FCS', 'HIC', 'IBD', 'IBT', 'IDA', 'IDB',
                  'IDX', 'INX', 'LIC', 'LMC', 'LMY', 'LTE', 'MIC', 'OSS', 'POST',
                  'PRE', 'PSS', 'PST', 'SST', 'SXZ', 'TSA', 'TSS', 'TEA', 'TEC',
                  'TLA', 'TMN', 'TSA', 'UMC', 'AFE', 'AFW', 'INX'}

    output = []
    for code in sorted(all_countries):
        if code in skip_codes:
            continue
        if code not in COUNTRY_COORDS:
            continue

        country_gdp = gdp.get(code, 0)
        country_pop = int(pop.get(code, 0))
        if country_gdp == 0 and country_pop == 0:
            continue

        coords = COUNTRY_COORDS[code]

        # Calculate asset values
        stocks = 0
        if code in mkt_pct and country_gdp:
            stocks = mkt_pct[code] / 100 * country_gdp

        bonds = 0
        if code in debt_pct and country_gdp:
            bonds = debt_pct[code] / 100 * country_gdp

        # Estimate real estate (roughly 2-4x GDP for most countries)
        re_multiplier = 3.0  # global average
        real_estate = country_gdp * re_multiplier

        # Use existing data if we have it (preserves billionaires, VC, etc.)
        if code in existing:
            entry = existing[code]
            # Update with fresh World Bank data
            entry['population'] = country_pop or entry.get('population', 0)
            entry['gdp_usd'] = country_gdp or entry.get('gdp_usd', 0)
            if stocks > 0:
                entry['breakdown']['stocks'] = int(stocks)
            if bonds > 0:
                entry['breakdown']['bonds'] = int(bonds)
            entry['total_capital_usd'] = sum(entry['breakdown'].values())
            output.append(entry)
        else:
            # New country — build from World Bank data
            # Get country name from World Bank
            breakdown = {}
            if real_estate > 0:
                breakdown['real_estate'] = int(real_estate)
            if stocks > 0:
                breakdown['stocks'] = int(stocks)
            if bonds > 0:
                breakdown['bonds'] = int(bonds)

            total = sum(breakdown.values())
            if total == 0:
                continue

            output.append({
                'country_code': code,
                'country_name': code,  # Will be updated below
                'lat': coords['lat'],
                'lng': coords['lng'],
                'population': country_pop,
                'gdp_usd': int(country_gdp),
                'total_capital_usd': total,
                'breakdown': breakdown,
            })

    # Fetch country names
    print("  Fetching country names...")
    names_resp = requests.get(f"{WB_BASE}/country/all?format=json&per_page=500", timeout=15)
    if names_resp.ok:
        names_data = names_resp.json()
        if len(names_data) >= 2:
            name_map = {c['id']: c['name'] for c in names_data[1]}
            for entry in output:
                if entry['country_name'] == entry['country_code']:
                    entry['country_name'] = name_map.get(entry['country_code'], entry['country_code'])

    output.sort(key=lambda c: c['total_capital_usd'], reverse=True)

    # Save
    for d in [DATA_DIR, STATIC_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        with open(d / 'globe_total.json', 'w') as f:
            json.dump(output, f)

    print(f"\nExpanded to {len(output)} countries (was {len(existing)})")
    print(f"Top 10: {', '.join(c['country_name'] + ' $' + str(round(c['total_capital_usd']/1e12,1)) + 'T' for c in output[:10])}")

    return output


if __name__ == '__main__':
    expand_countries()
