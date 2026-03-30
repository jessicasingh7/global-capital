"""Fetch stock market cap data using Exa search."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY, DATA_DIR


def fetch_market_caps():
    """Fetch stock market capitalization by country using Exa."""
    exa = Exa(api_key=EXA_API_KEY)

    results = exa.search_and_contents(
        "stock market capitalization by country 2025 2026 total market cap ranking",
        type="auto",
        num_results=5,
        text=True,
        summary=True,
    )

    market_caps = {}

    for result in results.results:
        text = (result.text or '') + ' ' + (result.summary or '')
        # Look for patterns like "United States: $50 trillion" or "Japan $6.5T"
        patterns = [
            r'(United States|China|Japan|United Kingdom|India|Canada|France|Germany|'
            r'South Korea|Australia|Switzerland|Saudi Arabia|Brazil|Italy|Netherlands|'
            r'Spain|Sweden|Singapore|Hong Kong|Israel|Indonesia|Mexico|Norway|'
            r'Russia|Turkey|South Africa|Nigeria|UAE|Qatar|Kuwait)'
            r'[:\s\-–—]+\$(\d+(?:\.\d+)?)\s*(trillion|T|billion|B)',
        ]
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                country = m.group(1)
                val = float(m.group(2))
                unit = m.group(3).lower()
                if unit in ('trillion', 't'):
                    val *= 1e12
                elif unit in ('billion', 'b'):
                    val *= 1e9
                market_caps[country] = int(val)

    return market_caps


def fetch_top_companies(country_name):
    """Fetch top companies by market cap for a specific country."""
    exa = Exa(api_key=EXA_API_KEY)

    results = exa.search_and_contents(
        f"largest companies {country_name} by market capitalization 2025 2026",
        type="auto",
        num_results=3,
        text=True,
        summary=True,
    )

    companies = []
    for result in results.results:
        text = (result.text or '') + ' ' + (result.summary or '')
        # Look for "Company Name ... $X billion/trillion"
        for m in re.finditer(
            r'([A-Z][A-Za-z\s&\.\'-]{2,30}?)[\s\-–—:]+\$(\d+(?:\.\d+)?)\s*(trillion|billion|T|B)\s*(?:market cap|capitalization)?',
            text
        ):
            name = m.group(1).strip()
            val = float(m.group(2))
            unit = m.group(3).lower()
            if unit in ('trillion', 't'):
                val *= 1e12
            else:
                val *= 1e9

            if name and val > 1e9 and not any(c['name'] == name for c in companies):
                companies.append({
                    'name': name,
                    'market_cap': int(val),
                    'cash': 0,
                })

    companies.sort(key=lambda c: c['market_cap'], reverse=True)
    return companies[:5]


if __name__ == '__main__':
    caps = fetch_market_caps()
    print(json.dumps(caps, indent=2))
    print(f"\nFound market caps for {len(caps)} countries")
