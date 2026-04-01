"""Fetch historical data from World Bank and IMF APIs."""

import json
import requests
from .config import DATA_DIR, STATIC_DATA_DIR
from .countries_meta import COUNTRIES

WB_BASE = "https://api.worldbank.org/v2"


def fetch_world_bank_indicator(indicator, start_year=1960, end_year=2025):
    """Fetch a World Bank indicator for all our countries."""
    codes = ';'.join(COUNTRIES.keys())
    url = f"{WB_BASE}/country/{codes}/indicator/{indicator}"
    params = {
        'date': f'{start_year}:{end_year}',
        'format': 'json',
        'per_page': 10000,
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if len(data) < 2:
        return {}

    # Organize by country and year
    by_country = {}
    for entry in data[1]:
        if entry['value'] is None:
            continue
        code = entry['countryiso3code']
        year = int(entry['date'])
        if code not in by_country:
            by_country[code] = {}
        by_country[code][year] = entry['value']

    return by_country


def fetch_historical_gdp():
    """Fetch GDP (current US$) by country, annual."""
    print("  Fetching GDP (NY.GDP.MKTP.CD)...")
    return fetch_world_bank_indicator('NY.GDP.MKTP.CD', 1960, 2025)


def fetch_historical_market_cap():
    """Fetch stock market capitalization (% of GDP) by country, annual."""
    print("  Fetching market cap % of GDP (CM.MKT.LCAP.GD.ZS)...")
    pct_data = fetch_world_bank_indicator('CM.MKT.LCAP.GD.ZS', 1975, 2025)

    # Also get GDP to convert % to absolute values
    print("  Converting to absolute values using GDP...")
    gdp_data = fetch_world_bank_indicator('NY.GDP.MKTP.CD', 1975, 2025)

    abs_data = {}
    for code in pct_data:
        abs_data[code] = {}
        for year in pct_data[code]:
            if code in gdp_data and year in gdp_data[code]:
                abs_data[code][year] = pct_data[code][year] / 100 * gdp_data[code][year]

    return abs_data


def fetch_historical_debt():
    """Fetch central government debt (% of GDP) from World Bank."""
    print("  Fetching government debt % of GDP (GC.DOD.TOTL.GD.ZS)...")
    pct_data = fetch_world_bank_indicator('GC.DOD.TOTL.GD.ZS', 1970, 2025)

    gdp_data = fetch_world_bank_indicator('NY.GDP.MKTP.CD', 1970, 2025)

    abs_data = {}
    for code in pct_data:
        abs_data[code] = {}
        for year in pct_data[code]:
            if code in gdp_data and year in gdp_data[code]:
                abs_data[code][year] = pct_data[code][year] / 100 * gdp_data[code][year]

    return abs_data


def fetch_all_historical():
    """Fetch all historical data and save as timeline JSON."""
    print("Fetching historical data from World Bank...")

    gdp = fetch_historical_gdp()
    market_cap = fetch_historical_market_cap()
    debt = fetch_historical_debt()

    # Build timeline: { year: { country_code: { gdp, stocks, bonds } } }
    all_years = set()
    for dataset in [gdp, market_cap, debt]:
        for code in dataset:
            all_years.update(dataset[code].keys())

    timeline = {}
    for year in sorted(all_years):
        if year < 1980:
            continue  # Too sparse before 1980
        timeline[str(year)] = {}
        for code in COUNTRIES:
            entry = {}
            if code in gdp and year in gdp[code]:
                entry['gdp'] = gdp[code][year]
            if code in market_cap and year in market_cap[code]:
                entry['stocks'] = market_cap[code][year]
            if code in debt and year in debt[code]:
                entry['bonds'] = debt[code][year]
            if entry:
                timeline[str(year)][code] = entry

    # Save
    for d in [DATA_DIR, STATIC_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        with open(d / 'historical.json', 'w') as f:
            json.dump(timeline, f)

    years = sorted(timeline.keys())
    print(f"  Saved historical.json: {len(years)} years ({years[0]}-{years[-1]})")
    print(f"  Countries with data: {len(set(c for y in timeline.values() for c in y))}")

    return timeline


if __name__ == '__main__':
    fetch_all_historical()
