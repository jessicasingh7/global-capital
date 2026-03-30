"""Fetch billionaire data using Exa search API."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY, DATA_DIR

COUNTRY_NAME_TO_CODE = {
    "united states": "USA", "us": "USA", "u.s.": "USA", "america": "USA",
    "china": "CHN", "hong kong": "HKG", "japan": "JPN",
    "united kingdom": "GBR", "uk": "GBR", "britain": "GBR",
    "germany": "DEU", "france": "FRA", "india": "IND",
    "canada": "CAN", "australia": "AUS", "south korea": "KOR",
    "brazil": "BRA", "italy": "ITA", "spain": "ESP",
    "mexico": "MEX", "indonesia": "IDN", "switzerland": "CHE",
    "netherlands": "NLD", "saudi arabia": "SAU",
    "uae": "ARE", "united arab emirates": "ARE",
    "singapore": "SGP", "norway": "NOR", "sweden": "SWE",
    "israel": "ISR", "russia": "RUS", "turkey": "TUR",
    "south africa": "ZAF", "nigeria": "NGA",
    "kuwait": "KWT", "qatar": "QAT",
}


def parse_worth(text):
    """Extract dollar amount from text like '$230 billion' or '$45.2B'."""
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(?:billion|bn|b)\b',
        r'\$(\d+(?:\.\d+)?)\s*(?:trillion|tn|t)\b',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 'trillion' in p or 'tn' in p or re.search(r'\bt\b', p):
                return int(val * 1e12)
            return int(val * 1e9)
    return 0


def guess_country_code(text):
    """Try to extract country from text."""
    text_lower = text.lower()
    for name, code in COUNTRY_NAME_TO_CODE.items():
        if name in text_lower:
            return code
    return None


def fetch_billionaires():
    """Fetch top billionaires per country using Exa."""
    exa = Exa(api_key=EXA_API_KEY)

    queries = [
        "Forbes billionaires list 2025 2026 richest people net worth",
        "Bloomberg billionaires index richest people world 2025 2026",
        "top billionaires by country net worth 2025",
    ]
    all_results = []
    for q in queries:
        try:
            r = exa.search_and_contents(q, type="auto", num_results=5, text=True, summary=True)
            all_results.extend(r.results)
        except Exception:
            pass
    results = type('R', (), {'results': all_results})()

    billionaires_by_country = {}

    for result in results.results:
        text = (result.text or '') + ' ' + (result.summary or '')
        # Try to find billionaire entries: "Name - $XXB - Source"
        lines = text.split('\n')
        for line in lines:
            worth = parse_worth(line)
            if worth < 1e9:
                continue
            # Try to extract name (usually at start of line)
            name_match = re.match(r'^(?:\d+[\.\)]\s*)?([A-Z][a-z]+ (?:[A-Z][a-z]+ )?(?:[A-Z][a-z]+))', line)
            if not name_match:
                continue
            name = name_match.group(1).strip()
            country_code = guess_country_code(line) or guess_country_code(text)
            if not country_code:
                continue

            if country_code not in billionaires_by_country:
                billionaires_by_country[country_code] = []

            # Avoid duplicates
            existing_names = [b['name'] for b in billionaires_by_country[country_code]]
            if name not in existing_names:
                source_match = re.search(r'(?:source[:\s]+|—\s*|–\s*)([^,\n$]+)', line, re.IGNORECASE)
                source = source_match.group(1).strip() if source_match else ''

                billionaires_by_country[country_code].append({
                    'name': name,
                    'worth': worth,
                    'source': source,
                })

    # Sort each country's billionaires by worth
    for code in billionaires_by_country:
        billionaires_by_country[code].sort(key=lambda b: b['worth'], reverse=True)

    return billionaires_by_country


if __name__ == '__main__':
    data = fetch_billionaires()
    print(json.dumps(data, indent=2))
    print(f"\nFound billionaires in {len(data)} countries")
    for code, bills in data.items():
        print(f"  {code}: {len(bills)} billionaires")
