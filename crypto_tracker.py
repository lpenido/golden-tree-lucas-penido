from datetime import datetime
import json
import os
from pathlib import Path
from typing import Dict, List

import requests
import pandas as pd


def get_api_response(api_url: str, headers: dict) -> List[Dict]:
    """Helper function to seperate API call from API response processing"""
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    data = response.json()["data"]
    return data


def save_csv(df: pd.DataFrame, save_path: Path):
    """Helper function to standardize saving mechanism for tables"""
    df.to_csv(save_path, index=False)
    print(f"File saved to {save_path}")


# Part 1: Store the entire universe of coins in a csv. This is for security data or coin level data.
def get_coin_universe(api_response: dict, save_path: Path) -> pd.DataFrame:
    """Get the universe of coins from CoinMarketCap."""
    # In production, keys for the universe can be handled by dictionary comprehension
    # or a dataclass. If keys were implicitly defined, then there could be silent changing schemas.
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
        for coin in api_response
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
def get_coins_to_track(coins_to_track_path: Path) -> List[str]:
    """Helper function to get all the coin symbols of interest."""
    # This read could be replaced with a "safe_read" helper function to get expected
    # and would be appropriate for larger workloads where failures during the process should be logged
    coins_to_track = pd.read_csv(coins_to_track_path)
    coins_to_track = coins_to_track["Symbol"].tolist()
    return coins_to_track


def is_top_currency(cmc_rank: int) -> bool:
    """Helper function to rank top currencies to track."""
    return cmc_rank <= 10


def get_pricing_data(coins_to_track_path: Path, df_universe: pd.DataFrame, save_dir: Path) -> pd.DataFrame:
    """Get and store pricing data for coins."""
    coin_ids = get_coins_to_track(coins_to_track_path)
    process_runtime = datetime.now().isoformat()

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
def analyze_bitcoin_relationship(
    df_pricing: pd.DataFrame, save_path: Path
) -> pd.DataFrame:
    """Analyze the relationship between bitcoin and other coins."""
    bitcoin_data = df_pricing[df_pricing["symbol"] == "BTC"]
    if bitcoin_data.empty:
        raise ValueError

    bitcoin_change = bitcoin_data.iloc[0]["percent_change_24h"]
    results = []
    for _, row in df_pricing.iterrows():
        if row["symbol"] != "BTC":
            diff = row["percent_change_24h"] - bitcoin_change
            results.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "percent_change_diff": diff,
                }
            )

    df_results = pd.DataFrame(results).sort_values(by="percent_change_diff")
    save_csv(df_results, save_path)
    print(f"Bitcoin relationship analysis saved to {save_path}")
    return df_results


# Part 4: Write a python function to output the average 24H percent change vs bitcoin for each
# currency over each run by parsing through the files you’ve generated.
def get_pricing_dfs(pricing_data_dir: Path) -> List[pd.DataFrame]:
    """Helper function in case sourcing for pricing data ever needs to change."""
    pricing_df_paths = pricing_data_dir.glob("*.csv")
    dfs_pricing = [pd.read_csv(f) for f in pricing_df_paths] # This read could be replaced with a "safe_read" helper function to check for propagating nans
    return dfs_pricing


def calculate_average_difference(dfs_pricing: List[pd.DataFrame]) -> pd.DataFrame:
    """Calculate the average 24H percent change difference vs. bitcoin."""
    all_data = pd.concat(dfs_pricing)
    bitcoin_data = all_data[all_data["symbol"] == "BTC"]
    if bitcoin_data.empty:
        raise ValueError

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

    df_averages = pd.DataFrame(averages)
    print(df_averages)
    return df_averages


def run_process():
    """A wrapper to call all steps in the tracking process"""
    try:
        df_universe = get_coin_universe(UNIVERSE_FILE)
        df_pricing = get_pricing_data(df_universe, PRICING_DATA_DIR)
        analyze_bitcoin_relationship(df_pricing, ANALYSIS_FILE)
    except requests.exceptions.HTTPError as e:
        print(f"API Request failed: {e}")
    except ValueError as e:
        print(f"Bitcoin data not found in pricing call. {e}")

    try:
        dfs_pricing = get_pricing_dfs(PRICING_DATA_DIR)
        calculate_average_difference(dfs_pricing)
    except ValueError as e:
        print(f"Bitcoin data not found across pricing files. {e}")


if __name__ == "__main__":
    run_process()
