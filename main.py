from datetime import datetime
from pathlib import Path

import requests
import pandas as pd


# Config
API_KEY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"  #  Sandbox api key
API_URL = "https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"  #  Sandbox listings
HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY,
}

# File paths
COINS_TO_TRACK_FILE = "coins_to_track.csv"
UNIVERSE_FILE = "coin_universe.csv"
PRICING_DATA_DIR = Path(__file__).parent / "pricing_data/"
ANALYSIS_FILE = "bitcoin_relationship.csv"


# Making sure directories exist
PRICING_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Part 1: Store the entire universe of coins in a csv. This is for security data or coin level data.
def get_coin_universe():
    """Get the universe of coins from CoinMarketCap."""
    response = requests.get(API_URL, headers=HEADERS)
    try:
        response.raise_for_status()
        data = response.json()["data"]
        universe = [{
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"],
            "slug": coin["slug"],
            "cmc_rank": coin["cmc_rank"],
            "num_market_pairs": coin["circulating_supply"],
            "circulating_supply": coin["circulating_supply"],
            "total_supply": coin["total_supply"],
            "max_supply": coin["max_supply"],
            "infinite_supply": coin["infinite_supply"],
            "last_updated": coin["last_updated"],
            "date_added": coin["date_added"],
            "tags": coin["tags"],
            "platform": coin["platform"],
            "self_reported_circulating_supply": coin["self_reported_circulating_supply"],
            "self_reported_market_cap": coin["self_reported_market_cap"],
            "quote": coin["quote"],
        } for coin in data]

        df_universe = pd.DataFrame(universe)
        df_universe.to_csv(UNIVERSE_FILE, index=False)
        print(f"Coin universe saved to {UNIVERSE_FILE}")
    except requests.exceptions.HTTPError as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    get_coin_universe()
