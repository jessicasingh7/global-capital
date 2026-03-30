"""Pipeline runner — fetches all data sources and writes JSON files."""

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.fetchers.config import DATA_DIR, STATIC_DATA_DIR
from pipeline.fetchers.countries_meta import COUNTRIES
from pipeline.fetchers.crypto import fetch_crypto
from pipeline.fetchers.billionaires import fetch_billionaires
from pipeline.fetchers.markets import fetch_market_caps
from pipeline.fetchers.sovereign_wealth import fetch_sovereign_wealth
from pipeline.fetchers.vc_deals import fetch_vc_data
from pipeline.fetchers.real_estate import fetch_real_estate
from pipeline.fetchers.bonds import fetch_bonds


def load_existing():
    """Load existing globe_total.json as baseline."""
    path = DATA_DIR / 'globe_total.json'
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        return {c['country_code']: c for c in data}
    return {}


def save_json(data, filename):
    """Write JSON to both data/ and static/data/."""
    for d in [DATA_DIR, STATIC_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        with open(d / filename, 'w') as f:
            json.dump(data, f)
    print(f"  Saved {filename}")


def run():
    print("=" * 50)
    print(f"Pipeline run: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 50)

    existing = load_existing()
    errors = []

    # 1. Crypto (CoinGecko — free, no key)
    print("\n[1/6] Fetching crypto from CoinGecko...")
    try:
        crypto = fetch_crypto()
        total_crypto = crypto['total_market_cap']
        print(f"  ${total_crypto/1e12:.2f}T total, BTC dominance {crypto['btc_dominance']}%")

        crypto_dist = {
            'USA': 0.32, 'CHN': 0.08, 'IND': 0.10, 'GBR': 0.04, 'BRA': 0.03,
            'IDN': 0.06, 'NGA': 0.05, 'TUR': 0.03, 'KOR': 0.04, 'JPN': 0.03,
            'DEU': 0.02, 'FRA': 0.02, 'CAN': 0.02, 'AUS': 0.02, 'RUS': 0.02,
            'MEX': 0.01, 'SGP': 0.01, 'ARE': 0.01, 'CHE': 0.01, 'HKG': 0.01,
            'ESP': 0.01, 'ITA': 0.01, 'NLD': 0.01, 'SWE': 0.01, 'ISR': 0.01,
            'ZAF': 0.01, 'NOR': 0.005, 'SAU': 0.005, 'KWT': 0.001, 'QAT': 0.001,
        }
        for code, pct in crypto_dist.items():
            if code in existing:
                existing[code]['breakdown']['crypto'] = int(total_crypto * pct)
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"crypto: {e}")

    # 2. Billionaires (Exa)
    print("\n[2/6] Fetching billionaires via Exa...")
    try:
        billionaires = fetch_billionaires()
        total_found = sum(len(b) for b in billionaires.values())
        print(f"  {total_found} billionaires across {len(billionaires)} countries")

        for code, bills in billionaires.items():
            if code in existing:
                existing[code]['top_billionaires'] = [
                    {'name': b['name'], 'worth': b['worth'], 'source': b['source']}
                    for b in bills[:5]
                ]
                existing[code]['num_billionaires'] = len(bills)
                total_worth = sum(b['worth'] for b in bills)
                if total_worth > 0:
                    existing[code]['breakdown']['billionaires'] = total_worth
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"billionaires: {e}")

    # 3. Stock markets (Exa)
    print("\n[3/6] Fetching stock market caps via Exa...")
    try:
        market_caps = fetch_market_caps()
        print(f"  Found {len(market_caps)} countries")

        name_to_code = {v['name']: k for k, v in COUNTRIES.items()}
        name_to_code.update({'United States': 'USA', 'South Korea': 'KOR',
                            'United Kingdom': 'GBR', 'Hong Kong': 'HKG',
                            'Saudi Arabia': 'SAU'})

        for name, cap in market_caps.items():
            code = name_to_code.get(name)
            if code and code in existing:
                existing[code]['breakdown']['stocks'] = cap
                print(f"    {name}: ${cap/1e12:.1f}T")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"markets: {e}")

    # 4. Sovereign wealth (Exa)
    print("\n[4/6] Fetching sovereign wealth funds via Exa...")
    try:
        swf = fetch_sovereign_wealth()
        print(f"  Found SWFs in {len(swf)} countries")
        for code, info in swf.items():
            if code in existing:
                existing[code]['breakdown']['sovereign_wealth'] = info['total']
                print(f"    {code}: ${info['total']/1e12:.2f}T")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"sovereign_wealth: {e}")

    # 5. Real estate (Exa)
    print("\n[5/6] Fetching real estate values via Exa...")
    try:
        real_estate = fetch_real_estate()
        print(f"  Found {len(real_estate)} countries")
        for code, val in real_estate.items():
            if code in existing:
                existing[code]['breakdown']['real_estate'] = val
                print(f"    {code}: ${val/1e12:.1f}T")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"real_estate: {e}")

    # 6. Government debt (Exa)
    print("\n[6/6] Fetching government debt via Exa...")
    try:
        bonds = fetch_bonds()
        print(f"  Found {len(bonds)} countries")
        for code, val in bonds.items():
            if code in existing:
                existing[code]['breakdown']['bonds'] = val
                print(f"    {code}: ${val/1e12:.1f}T")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(f"bonds: {e}")

    # Note: VC data fetches per-country and uses many API calls.
    # Run separately with: python -m pipeline.fetchers.vc_deals
    # For now, keep existing VC data.

    # Recalculate totals
    print("\nRecalculating totals...")
    for code, country in existing.items():
        country['total_capital_usd'] = sum(country['breakdown'].values())

    output = sorted(existing.values(), key=lambda c: c['total_capital_usd'], reverse=True)

    save_json(output, 'globe_total.json')

    # Scale totals
    asset_keys = ['real_estate', 'bonds', 'stocks', 'pensions', 'billionaires',
                  'pe_hf', 'sovereign_wealth', 'central_bank', 'crypto']
    asset_meta = {
        'real_estate': ('Real Estate', '#0EF3C5'),
        'bonds': ('Bonds & Debt', '#025385'),
        'stocks': ('Stock Markets', '#38bdf8'),
        'pensions': ('Pension Funds', '#fb923c'),
        'billionaires': ('Billionaires', '#fbbf24'),
        'pe_hf': ('PE & Hedge Funds', '#f43f5e'),
        'sovereign_wealth': ('Sovereign Wealth', '#04E2B7'),
        'central_bank': ('Central Banks', '#038298'),
        'crypto': ('Crypto', '#e879f9'),
    }

    scale = {
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'asset_classes': [
            {
                'name': asset_meta[k][0], 'key': k,
                'total_usd': sum(c['breakdown'].get(k, 0) for c in output),
                'color': asset_meta[k][1],
            }
            for k in asset_keys
            if sum(c['breakdown'].get(k, 0) for c in output) > 0
        ]
    }
    scale['asset_classes'].sort(key=lambda a: a['total_usd'], reverse=True)
    save_json(scale, 'scale_totals.json')

    status = {
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'status': 'success' if not errors else 'partial',
        'errors': errors,
    }
    save_json(status, 'status.json')

    grand_total = sum(c['total_capital_usd'] for c in output)
    print(f"\nGrand total: ${grand_total/1e12:.1f}T across {len(output)} countries")
    print(f"Done! {'Errors: ' + ', '.join(errors) if errors else 'All successful.'}")


if __name__ == '__main__':
    run()
