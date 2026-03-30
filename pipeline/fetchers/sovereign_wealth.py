"""Fetch sovereign wealth fund data using Exa."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY


def fetch_sovereign_wealth():
    """Fetch sovereign wealth fund data by country."""
    exa = Exa(api_key=EXA_API_KEY)

    results = exa.search_and_contents(
        "largest sovereign wealth funds world ranking 2025 2026 assets under management by country",
        type="auto",
        num_results=10,
        text=True,
    )

    funds = {}
    for result in results.results:
        text = result.text or ''
        # Match patterns like "Norway Government Pension Fund Global $1.7 trillion"
        for m in re.finditer(
            r'([\w\s\'-]+(?:Fund|Investment Authority|Corporation|Reserve|GIC|ADIA|KIA|PIF|QIA|CIC|SAFE|NBIM|Temasek|Mubadala)[\w\s]*?)'
            r'[\s\-–—:]+\$(\d+(?:\.\d+)?)\s*(trillion|billion|T|B)',
            text, re.IGNORECASE
        ):
            name = m.group(1).strip()
            val = float(m.group(2))
            unit = m.group(3).lower()
            if unit in ('trillion', 't'):
                val *= 1e12
            else:
                val *= 1e9

            # Map fund to country
            fund_country = {
                'norway': 'NOR', 'norwegian': 'NOR', 'nbim': 'NOR', 'pension fund global': 'NOR',
                'china': 'CHN', 'cic': 'CHN', 'safe': 'CHN',
                'abu dhabi': 'ARE', 'adia': 'ARE', 'mubadala': 'ARE',
                'kuwait': 'KWT', 'kia': 'KWT',
                'saudi': 'SAU', 'pif': 'SAU',
                'singapore': 'SGP', 'gic': 'SGP', 'temasek': 'SGP',
                'qatar': 'QAT', 'qia': 'QAT',
                'hong kong': 'HKG',
                'australia': 'AUS', 'future fund': 'AUS',
                'russia': 'RUS',
                'south korea': 'KOR', 'korea': 'KOR',
            }
            code = None
            name_lower = name.lower()
            for key, c in fund_country.items():
                if key in name_lower:
                    code = c
                    break

            if code and val > 1e9:
                if code not in funds:
                    funds[code] = {'total': 0, 'funds': []}
                funds[code]['funds'].append({'name': name[:50], 'aum': int(val)})
                funds[code]['total'] += int(val)

    # Deduplicate and sort
    for code in funds:
        seen = set()
        unique = []
        for f in funds[code]['funds']:
            if f['name'] not in seen:
                seen.add(f['name'])
                unique.append(f)
        funds[code]['funds'] = sorted(unique, key=lambda f: f['aum'], reverse=True)
        funds[code]['total'] = sum(f['aum'] for f in funds[code]['funds'])

    return funds


if __name__ == '__main__':
    data = fetch_sovereign_wealth()
    print(json.dumps(data, indent=2))
    for code, info in data.items():
        print(f"  {code}: ${info['total']/1e12:.2f}T — {', '.join(f['name'] for f in info['funds'][:3])}")
