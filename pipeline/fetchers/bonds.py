"""Fetch government debt/bond data using Exa."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY


def fetch_bonds():
    """Fetch government debt by country using Exa."""
    exa = Exa(api_key=EXA_API_KEY)

    results = exa.search_and_contents(
        "government debt by country 2025 2026 national debt total outstanding bonds trillion ranking",
        type="auto",
        num_results=10,
        text=True,
    )

    debt_by_country = {}
    country_map = {
        'united states': 'USA', 'us': 'USA', 'u.s.': 'USA',
        'china': 'CHN', 'japan': 'JPN',
        'united kingdom': 'GBR', 'uk': 'GBR',
        'germany': 'DEU', 'france': 'FRA', 'india': 'IND',
        'canada': 'CAN', 'australia': 'AUS', 'south korea': 'KOR',
        'brazil': 'BRA', 'italy': 'ITA', 'spain': 'ESP',
        'mexico': 'MEX', 'indonesia': 'IDN', 'switzerland': 'CHE',
        'netherlands': 'NLD', 'saudi arabia': 'SAU',
        'singapore': 'SGP', 'norway': 'NOR', 'sweden': 'SWE',
        'israel': 'ISR', 'russia': 'RUS', 'turkey': 'TUR',
        'south africa': 'ZAF', 'nigeria': 'NGA',
    }

    for result in results.results:
        text = result.text or ''
        for m in re.finditer(
            r'([\w\s\.]+?)[\s:–—\-]+\$(\d+(?:\.\d+)?)\s*(trillion|T|billion|B)',
            text, re.IGNORECASE
        ):
            country_text = m.group(1).strip().lower()
            val = float(m.group(2))
            unit = m.group(3).lower()
            if unit in ('trillion', 't'):
                val *= 1e12
            else:
                val *= 1e9

            code = country_map.get(country_text)
            if code and val > 1e9:
                if code not in debt_by_country or val > debt_by_country[code]:
                    debt_by_country[code] = int(val)

    return debt_by_country


if __name__ == '__main__':
    data = fetch_bonds()
    print(json.dumps(data, indent=2))
    for code, val in sorted(data.items(), key=lambda x: x[1], reverse=True):
        print(f"  {code}: ${val/1e12:.1f}T")
