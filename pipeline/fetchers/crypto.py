"""Fetch crypto market data from CoinGecko (free, no API key)."""

import json
import requests
from .config import DATA_DIR

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def fetch_crypto():
    """Fetch global crypto market cap and top coins."""
    # Global market data
    global_resp = requests.get(f"{COINGECKO_BASE}/global", timeout=10)
    global_resp.raise_for_status()
    global_data = global_resp.json()['data']

    total_market_cap = global_data['total_market_cap'].get('usd', 0)
    total_volume = global_data['total_volume'].get('usd', 0)
    btc_dominance = global_data.get('market_cap_percentage', {}).get('btc', 0)

    # Top 20 coins
    coins_resp = requests.get(
        f"{COINGECKO_BASE}/coins/markets",
        params={
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 20,
            'page': 1,
        },
        timeout=10,
    )
    coins_resp.raise_for_status()
    coins = coins_resp.json()

    top_coins = [
        {
            'name': c['name'],
            'symbol': c['symbol'].upper(),
            'market_cap': c.get('market_cap', 0),
            'price': c.get('current_price', 0),
            'change_24h': round(c.get('price_change_percentage_24h', 0) or 0, 2),
        }
        for c in coins
    ]

    return {
        'total_market_cap': total_market_cap,
        'total_volume_24h': total_volume,
        'btc_dominance': round(btc_dominance, 1),
        'top_coins': top_coins,
    }


if __name__ == '__main__':
    data = fetch_crypto()
    print(json.dumps(data, indent=2))
    print(f"\nTotal crypto market cap: ${data['total_market_cap']/1e12:.2f}T")
    print(f"BTC dominance: {data['btc_dominance']}%")
