"""Fetch VC/startup funding data using Exa."""

import json
import re
from exa_py import Exa
from .config import EXA_API_KEY
from .countries_meta import COUNTRIES


def fetch_vc_data():
    """Fetch VC deal activity by country using Exa."""
    exa = Exa(api_key=EXA_API_KEY)

    vc_by_country = {}

    # Search for top VC markets
    for country_code, meta in COUNTRIES.items():
        country_name = meta['name']

        results = exa.search_and_contents(
            f"venture capital startup funding {country_name} 2025 2026 total investment deals raised",
            type="auto",
            num_results=3,
            text=True,
            summary=True,
        )

        total_annual = 0
        num_deals = 0
        sectors = set()
        notable_rounds = []

        for result in results.results:
            text = (result.text or '') + ' ' + (result.summary or '')

            # Try to find total annual VC investment
            for m in re.finditer(
                r'\$(\d+(?:\.\d+)?)\s*(billion|B|million|M)\s*(?:in|of)?\s*(?:venture|vc|startup|funding|investment)',
                text, re.IGNORECASE
            ):
                val = float(m.group(1))
                unit = m.group(2).lower()
                if unit in ('billion', 'b'):
                    val *= 1e9
                elif unit in ('million', 'm'):
                    val *= 1e6
                if val > total_annual:
                    total_annual = int(val)

            # Try to find deal count
            for m in re.finditer(r'(\d{1,5}(?:,\d{3})?)\s*(?:deals|rounds|investments|transactions)', text, re.IGNORECASE):
                count = int(m.group(1).replace(',', ''))
                if count > num_deals:
                    num_deals = count

            # Extract sectors
            sector_keywords = ['AI', 'ML', 'Fintech', 'Health Tech', 'Climate Tech', 'SaaS',
                             'Biotech', 'Crypto', 'Web3', 'E-commerce', 'EdTech', 'Deep Tech',
                             'Robotics', 'Clean Tech', 'Cybersecurity', 'Gaming', 'AgTech',
                             'PropTech', 'Logistics', 'Space', 'Autonomous', 'EV', 'Battery',
                             'Semiconductors', 'Enterprise']
            for s in sector_keywords:
                if s.lower() in text.lower():
                    sectors.add(s)

            # Find notable rounds
            for m in re.finditer(
                r'([A-Z][A-Za-z\s\.]{2,25}?)\s*(?:raised|secured|closed)\s*\$(\d+(?:\.\d+)?)\s*(billion|B|million|M)',
                text, re.IGNORECASE
            ):
                company = m.group(1).strip()
                val = float(m.group(2))
                unit = m.group(3).lower()
                if unit in ('billion', 'b'):
                    val *= 1e9
                else:
                    val *= 1e6
                if val >= 50e6 and not any(r['company'] == company for r in notable_rounds):
                    notable_rounds.append({
                        'company': company,
                        'amount': int(val),
                        'sector': '',
                    })

        if total_annual > 0 or num_deals > 0 or notable_rounds:
            notable_rounds.sort(key=lambda r: r['amount'], reverse=True)
            vc_by_country[country_code] = {
                'total_annual_usd': total_annual,
                'num_deals': num_deals,
                'top_sectors': list(sectors)[:5] or ['Tech'],
                'notable_rounds': notable_rounds[:3],
            }

    return vc_by_country


if __name__ == '__main__':
    data = fetch_vc_data()
    print(json.dumps(data, indent=2))
    print(f"\nFound VC data for {len(data)} countries")
    for code, info in sorted(data.items(), key=lambda x: x[1]['total_annual_usd'], reverse=True):
        print(f"  {code}: ${info['total_annual_usd']/1e9:.1f}B/yr, {info['num_deals']} deals")
