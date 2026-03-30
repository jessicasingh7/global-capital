"""Fetch real estate market data using Exa + known distributions."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY

# Known approximate distribution of global real estate by country
# Source: Savills, McKinsey Global Institute estimates
RE_DISTRIBUTION = {
    'CHN': 0.28, 'USA': 0.14, 'JPN': 0.06, 'GBR': 0.04, 'DEU': 0.04,
    'FRA': 0.04, 'IND': 0.04, 'ITA': 0.03, 'CAN': 0.02, 'AUS': 0.03,
    'KOR': 0.02, 'ESP': 0.02, 'BRA': 0.02, 'RUS': 0.01, 'MEX': 0.01,
    'IDN': 0.01, 'CHE': 0.01, 'NLD': 0.01, 'SAU': 0.01, 'ARE': 0.005,
    'SGP': 0.005, 'NOR': 0.003, 'SWE': 0.005, 'ISR': 0.003, 'HKG': 0.01,
    'TUR': 0.01, 'ZAF': 0.003, 'NGA': 0.003, 'KWT': 0.001, 'QAT': 0.001,
}


def fetch_real_estate():
    """Fetch global real estate total via Exa, then distribute by country."""
    exa = Exa(api_key=EXA_API_KEY)

    results = exa.search_and_contents(
        "global real estate total value 2025 2026 trillion Savills",
        type="auto",
        num_results=5,
        text=True,
    )

    global_total = 380e12  # default fallback

    for result in results.results:
        text = result.text or ''
        # Look for "$XXX trillion" in context of real estate
        for m in re.finditer(r'\$(\d+(?:\.\d+)?)\s*(trillion|T)', text, re.IGNORECASE):
            val = float(m.group(1)) * 1e12
            if 200e12 < val < 600e12:  # sanity check — should be $200T-$600T range
                global_total = val
                break

    print(f"  Global real estate total: ${global_total/1e12:.1f}T")

    # Distribute across countries
    re_by_country = {}
    for code, pct in RE_DISTRIBUTION.items():
        re_by_country[code] = int(global_total * pct)

    return re_by_country


if __name__ == '__main__':
    data = fetch_real_estate()
    print(json.dumps({k: f"${v/1e12:.1f}T" for k, v in data.items()}, indent=2))
