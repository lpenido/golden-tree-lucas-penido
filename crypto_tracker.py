from datetime import datetime
import json
import os
from pathlib import Path

import requests
import pandas as pd


# Config
API_KEY = json.load(open("secrets.json", "r"))["api_key"]
API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
HEADERS = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": API_KEY,
}

# File paths
ROOT_DIR = Path(__file__).parent
COINS_TO_TRACK_FILE = ROOT_DIR / "coins_to_track.csv"
UNIVERSE_FILE = "coin_universe.csv"
PRICING_DATA_DIR = ROOT_DIR / "pricing_data/"
ANALYSIS_FILE = "bitcoin_relationship.csv"


# Making sure directories exist
PRICING_DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_csv(df: pd.DataFrame, save_path: Path):
    """Helper function to standardize saving mechanism for tables"""
    df.to_csv(save_path, index=False)
    print(f"File saved to {save_path}")


# Part 1: Store the entire universe of coins in a csv. This is for security data or coin level data.
def get_coin_universe(save_path: Path) -> pd.DataFrame      :
    """Get the universe of coins from CoinMarketCap."""
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()["data"]
    universe = [
        {
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
            "self_reported_circulating_supply": coin[
                "self_reported_circulating_supply"
            ],
            "self_reported_market_cap": coin["self_reported_market_cap"],
            "quote": coin["quote"],
        }
        for coin in data
    ]

    # Adding percent_change_24h from quotes
    for coin in universe:
        coin["percent_change_24h"] = coin["quote"]["USD"]["percent_change_24h"]

    df_universe = pd.DataFrame(universe)
    save_csv(df_universe, save_path)
    print(f"Coin universe saved to {save_path}")
    return df_universe



# Part 2: Read coins_to_track.csv and get pricing data for each coin. Store the pricing data in a
# csv. Each time your process runs a new csv should be generated and a timestamp
# should be appended to the file name.
#       a. When you load the data, add a “LoadedWhen” column with the current date time.
#       b . When you load the data, add an “IsTopCurrency” column that is true when the
#       cmc_rank is less than or equal to 10, false otherwise.
def get_coins_to_track() -> list:
    """Helper function to get all the coin symbols of interest."""
    coins_to_track = pd.read_csv(COINS_TO_TRACK_FILE)
    coins_to_track = coins_to_track["Symbol"].tolist()
    return coins_to_track

def is_top_currency(cmc_rank: int) -> bool:
    return cmc_rank <= 10

def get_pricing_data(universe_file: Path, save_dir: Path) -> pd.DataFrame:
    """Get and store pricing data for coins."""
    coin_ids = get_coins_to_track()

    process_runtime = datetime.now().isoformat()
    df_universe = pd.read_csv(universe_file)
    df_pricing = df_universe[
        (df_universe["symbol"].isin(coin_ids)) | (df_universe["symbol"] == "BTC")
    ].copy()  # to make sure BTC is always included
    df_pricing["LoadedWhen"] = process_runtime
    df_pricing["IsTopCurrency"] = df_pricing["cmc_rank"].map(is_top_currency)

    save_path = save_dir / f"pricing_data__{process_runtime}.csv"
    save_csv(df_pricing, save_path)
    print(f"Coin pricing saved to {save_dir}")
    return df_pricing


# Part 3: You should use the data you’ve loaded to produce a csv that tracks the relationship
# between bitcoin and the coins we are analyzing. The csv should have these columns:
#       a. Timestamp of the analysis.
#       b. The difference in 24H percent change between bitcoin and the currency we’re
#          evaluating.
#       c. Sorted from smallest difference to largest.
def get_most_recent_file(dir_path: Path) -> Path:
    """Helper function to get most recent csv in pricing dir."""
    dir_csvs = sorted(
        dir_path.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
    )  # reverse = True is DESC
    return dir_csvs[0]


def analyze_bitcoin_relationship() -> pd.DataFrame:
    """Analyze the relationship between bitcoin and other coins."""
    pricing_data = get_most_recent_file(PRICING_DATA_DIR)
    df_pricing = pd.read_csv(pricing_data)
    bitcoin_data = df_pricing[df_pricing["symbol"] == "BTC"]

    bitcoin_change = bitcoin_data.iloc[0]["percent_change_24h"]
    results = []
    for _, row in df_pricing.iterrows():
        if row["symbol"] != "BTC":
            diff = abs(row["percent_change_24h"] - bitcoin_change)
            results.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "percent_change_diff": diff,
                }
            )

    df_results = pd.DataFrame(results).sort_values(by="percent_change_diff")
    save_csv(df_results, ANALYSIS_FILE)
    print(f"Bitcoin relationship analysis saved to {ANALYSIS_FILE}")
    return df_results


# Part 4: Write a python function to output the average 24H percent change vs bitcoin for each
# currency over each run by parsing through the files you’ve generated.
def get_pricing_files() -> list:
    """Helper function in case sourcing for pricing data ever needs to change."""
    return PRICING_DATA_DIR.glob("*.csv")


def calculate_average_difference() -> pd.DataFrame:
    """Calculate the average 24H percent change difference vs. bitcoin."""
    pricing_files = get_pricing_files()
    all_data = pd.concat((pd.read_csv(f) for f in pricing_files))
    bitcoin_data = all_data[all_data["symbol"] == "BTC"]

    bitcoin_change = bitcoin_data["percent_change_24h"].mean()
    averages = []

    for symbol in all_data["symbol"].unique():
        if symbol != "BTC":
            symbol_data = all_data[all_data["symbol"] == symbol]
            avg_change = symbol_data["percent_change_24h"].mean()
            averages.append(
                {
                    "symbol": symbol,
                    "average_diff_vs_bitcoin": avg_change - bitcoin_change,
                }
            )

    # Cutting down output to only tracked coins
    df_averages = pd.DataFrame(averages)
    print(df_averages)
    return df_averages


def run_process():
    """A wrapper to call all steps in the tracking process"""
    try:
        get_coin_universe(UNIVERSE_FILE)
        get_pricing_data(UNIVERSE_FILE, PRICING_DATA_DIR)
        analyze_bitcoin_relationship()
        calculate_average_difference()
    except requests.exceptions.HTTPError as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    run_process()
