from pathlib import Path
import shutil
import os
from unittest.mock import patch, Mock

import pytest
import pandas as pd

from crypto_tracker import (
    safe_save_file_name,
    get_coin_universe,
    get_coins_to_track,
    is_top_currency,
    get_pricing_data,
    analyze_bitcoin_relationship,
    get_pricing_dfs,
    calculate_average_difference,
    run_process
)


@pytest.fixture
def mock_coin_universe_response():
    return [
            {
                "id": 1,
                "name": "Bitcoin",
                "symbol": "BTC",
                "slug": "bitcoin",
                "num_market_pairs": 11869,
                "date_added": "2010-07-13T00:00:00.000Z",
                "tags": [
                    "mineable",
                    "pow",
                    "sha-256",
                    "store-of-value",
                    "state-channel",
                    "coinbase-ventures-portfolio",
                    "three-arrows-capital-portfolio",
                    "polychain-capital-portfolio",
                    "binance-labs-portfolio",
                    "blockchain-capital-portfolio",
                    "boostvc-portfolio",
                    "cms-holdings-portfolio",
                    "dcg-portfolio",
                    "dragonfly-capital-portfolio",
                    "electric-capital-portfolio",
                    "fabric-ventures-portfolio",
                    "framework-ventures-portfolio",
                    "galaxy-digital-portfolio",
                    "huobi-capital-portfolio",
                    "alameda-research-portfolio",
                    "a16z-portfolio",
                    "1confirmation-portfolio",
                    "winklevoss-capital-portfolio",
                    "usv-portfolio",
                    "placeholder-ventures-portfolio",
                    "pantera-capital-portfolio",
                    "multicoin-capital-portfolio",
                    "paradigm-portfolio",
                    "bitcoin-ecosystem",
                    "ftx-bankruptcy-estate",
                    "2017-2018-alt-season",
                ],
                "max_supply": 21000000,
                "circulating_supply": 19812890,
                "total_supply": 19812890,
                "infinite_supply": False,
                "platform": None,
                "cmc_rank": 1,
                "self_reported_circulating_supply": None,
                "self_reported_market_cap": None,
                "tvl_ratio": None,
                "last_updated": "2025-01-20T23:01:00.000Z",
                "quote": {
                    "USD": {
                        "price": 103325.80885486708,
                        "volume_24h": 133037548480.13788,
                        "volume_change_24h": 93.7051,
                        "percent_change_1h": 1.02022321,
                        "percent_change_24h": 0.69860286,
                        "percent_change_7d": 9.67106845,
                        "percent_change_30d": 6.4215294,
                        "percent_change_60d": 4.92526738,
                        "percent_change_90d": 52.55814934,
                        "market_cap": 2047182885002.5073,
                        "market_cap_dominance": 57.2814,
                        "fully_diluted_market_cap": 2169841985952.21,
                        "tvl": None,
                        "last_updated": "2025-01-20T23:01:00.000Z",
                    }
                },
            },
            {
                "id": 1027,
                "name": "Ethereum",
                "symbol": "ETH",
                "slug": "ethereum",
                "num_market_pairs": 9842,
                "date_added": "2015-08-07T00:00:00.000Z",
                "tags": [
                    "pos",
                    "smart-contracts",
                    "ethereum-ecosystem",
                    "coinbase-ventures-portfolio",
                    "three-arrows-capital-portfolio",
                    "polychain-capital-portfolio",
                    "heco-ecosystem",
                    "binance-labs-portfolio",
                    "avalanche-ecosystem",
                    "solana-ecosystem",
                    "blockchain-capital-portfolio",
                    "boostvc-portfolio",
                    "cms-holdings-portfolio",
                    "dcg-portfolio",
                    "dragonfly-capital-portfolio",
                    "electric-capital-portfolio",
                    "fabric-ventures-portfolio",
                    "framework-ventures-portfolio",
                    "hashkey-capital-portfolio",
                    "kenetic-capital-portfolio",
                    "huobi-capital-portfolio",
                    "alameda-research-portfolio",
                    "a16z-portfolio",
                    "1confirmation-portfolio",
                    "winklevoss-capital-portfolio",
                    "usv-portfolio",
                    "placeholder-ventures-portfolio",
                    "pantera-capital-portfolio",
                    "multicoin-capital-portfolio",
                    "paradigm-portfolio",
                    "tezos-ecosystem",
                    "near-protocol-ecosystem",
                    "bnb-chain-ecosystem",
                    "velas-ecosystem",
                    "ethereum-pow-ecosystem",
                    "osmosis-ecosystem",
                    "layer-1",
                    "ftx-bankruptcy-estate",
                    "zksync-era-ecosystem",
                    "viction-ecosystem",
                    "klaytn-ecosystem",
                    "sora-ecosystem",
                    "rsk-rbtc-ecosystem",
                    "starknet-ecosystem",
                ],
                "max_supply": None,
                "circulating_supply": 120501725.21190895,
                "total_supply": 120501725.21190895,
                "infinite_supply": True,
                "platform": None,
                "cmc_rank": 2,
                "self_reported_circulating_supply": None,
                "self_reported_market_cap": None,
                "tvl_ratio": None,
                "last_updated": "2025-01-20T23:02:00.000Z",
                "quote": {
                    "USD": {
                        "price": 3305.290787681842,
                        "volume_24h": 55416687850.433754,
                        "volume_change_24h": 2.1574,
                        "percent_change_1h": 0.94068359,
                        "percent_change_24h": 2.58135749,
                        "percent_change_7d": 5.71785649,
                        "percent_change_30d": -0.65987165,
                        "percent_change_60d": -1.93840292,
                        "percent_change_90d": 25.34849309,
                        "market_cap": 398293242242.69147,
                        "market_cap_dominance": 11.1404,
                        "fully_diluted_market_cap": 398293242242.69,
                        "tvl": None,
                        "last_updated": "2025-01-20T23:02:00.000Z",
                    }
                },
            },
        ]


@pytest.fixture
def mock_universe_file():
    test_universe_file = Path("test_coin_universe.csv")
    yield test_universe_file
    test_universe_file.unlink(missing_ok=True)


@pytest.fixture
def mock_df_universe():
    test_df_universe = pd.DataFrame(
        [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "cmc_rank": 1,
                "percent_change_24h": 0.69860286,
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "cmc_rank": 2,
                "percent_change_24h": 2.58135749,
            },
        ]
    )
    yield test_df_universe

@pytest.fixture
def mock_coins_to_track_file():
    test_coins_to_track = Path("test_coins_to_track.csv")
    pd.DataFrame(
        [
            {
                "Symbol": "BTC",
            },
            {
                "Symbol": "ETH",
            },
        ]
    ).to_csv(test_coins_to_track, index=False)
    yield test_coins_to_track
    test_coins_to_track.unlink(missing_ok=True)

@pytest.fixture
def mock_pricing_data_dir():
    test_pricing_data_dir = Path("test_pricing_data")
    test_pricing_data_dir.mkdir(parents=True, exist_ok=True)
    yield test_pricing_data_dir
    shutil.rmtree(test_pricing_data_dir)


@pytest.fixture
def mock_pricing_data_dir_populated():
    test_pricing_data_dir = Path("test_pricing_data")
    test_pricing_data_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "cmc_rank": 1,
                "percent_change_24h": 10,
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "cmc_rank": 2,
                "percent_change_24h": 20,
            },
        ]
    ).to_csv(test_pricing_data_dir / "test_pricing_older.csv", index=False)
    pd.DataFrame(
        [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "cmc_rank": 1,
                "percent_change_24h": 10,
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "cmc_rank": 2,
                "percent_change_24h": 30,
            },
        ]
    ).to_csv(test_pricing_data_dir / "test_pricing_newer.csv", index=False)
    yield test_pricing_data_dir
    shutil.rmtree(test_pricing_data_dir)


@pytest.fixture
def mock_df_pricing():
    test_df_pricing = pd.DataFrame(
        [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "cmc_rank": 1,
                "percent_change_24h": 0.69860286,
                "LoadedWhen": "2025-01-20T11:53:13.706530",
                "IsTopCurrency": True,
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "cmc_rank": 2,
                "percent_change_24h": 2.58135749,
                "LoadedWhen": "2025-01-20T11:53:13.706530",
                "IsTopCurrency": True,
            },
        ]
    )
    yield test_df_pricing


@pytest.fixture
def mock_analysis_save_path():
    test_analysis_save_path = Path("bitcoin_relationship.csv")
    yield test_analysis_save_path
    test_analysis_save_path.unlink(missing_ok=True)


def test_safe_save_file_name():
    """Testing to make sure there are no prohibitted characters in file names"""
    prohibitted_windows_characters = r'\/:*?"<>|'
    safe_name = safe_save_file_name("pricing_data__2025-01-20T16:00:48.458138.csv")
    assert safe_name == "pricing_data__2025-01-20T16_00_48.458138.csv"
    assert not any(char in safe_name for char in prohibitted_windows_characters)
    
    safe_name2 = safe_save_file_name("pricing_data__2025_01_22T15_55_01_087317.csv")
    assert safe_name2 == "pricing_data__2025_01_22T15_55_01_087317.csv"
    assert not any(char in safe_name2 for char in prohibitted_windows_characters)

def test_get_coin_universe(mock_coin_universe_response, mock_universe_file):
    """Testing the schema saves"""
    get_coin_universe(mock_coin_universe_response, mock_universe_file)

    assert mock_universe_file.exists() == True
    df = pd.read_csv(mock_universe_file)
    assert len(df) == 2
    primary_columns = ["name", "symbol", "percent_change_24h"]
    assert all(col in df.columns for col in primary_columns)
    assert "BTC" in df["symbol"].values
    assert "ETH" in df["symbol"].values


def test_get_coins_to_track(mock_coins_to_track_file):
    """Making sure the file to track coins exists and has at least BTC in it"""
    coins_to_track = get_coins_to_track(mock_coins_to_track_file)
    assert len(coins_to_track) > 0
    assert "BTC" in coins_to_track


def test_is_top_currency():
    """Testing if helper can tell Top 10"""
    assert is_top_currency(1) == True
    assert is_top_currency(10) == True
    assert is_top_currency(11) == False


def test_get_pricing_data(mock_coins_to_track_file, mock_df_universe, mock_pricing_data_dir):
    """Making sure pricing is the right content, type, and columns and that a file gets saved to the directory"""
    df_pricing = get_pricing_data(mock_coins_to_track_file, mock_df_universe, mock_pricing_data_dir)

    assert df_pricing.empty == False
    assert "LoadedWhen" in df_pricing.columns
    assert "IsTopCurrency" in df_pricing.columns
    assert "ETH" in df_pricing["symbol"].unique()

    pricing_data_dir_contents = list(mock_pricing_data_dir.glob("*.csv"))
    assert len(pricing_data_dir_contents) > 0


def test_analyze_bitcoin_relationship(
    mock_df_pricing, mock_pricing_data_dir, mock_analysis_save_path
):
    """Making sure BTC isn't reported as a benchmark against itself, that analysis column exists, analysis is correct, and file is made"""
    df_results = analyze_bitcoin_relationship(mock_df_pricing, mock_analysis_save_path)

    assert "BTC" not in df_results["symbol"].unique()
    assert "percent_change_diff" in df_results.columns
    assert round(df_results["percent_change_diff"].iloc[0], 2) == 1.88
    assert mock_analysis_save_path.exists() == True

    no_bitcoin_data = mock_df_pricing[~(mock_df_pricing["symbol"] == "BTC")]
    try:
        analyze_bitcoin_relationship(no_bitcoin_data, mock_analysis_save_path)
        assert False
    except ValueError:
        assert True


def test_get_pricing_dfs(mock_pricing_data_dir_populated):
    """Check if function can read csvs from directory into a list"""
    dfs = get_pricing_dfs(mock_pricing_data_dir_populated)
    assert len(dfs) == 2


def test_calculate_average_difference(mock_pricing_data_dir_populated):
    """Checking if function will take list, return df, and do the proper math"""
    dfs_pricing = get_pricing_dfs(mock_pricing_data_dir_populated)
    df_average = calculate_average_difference(dfs_pricing)
    assert df_average["average_diff_vs_bitcoin"].iloc[0] == 15


def test_no_pricing_files_calculate_average():
    """If provided an empty list, the function should raise a ValueError"""
    try:
        calculate_average_difference([])
        assert False
    except ValueError:
        assert True

def test_run_process(mock_universe_file, mock_coins_to_track_file, mock_pricing_data_dir, mock_analysis_save_path):
    """Tests if process can run with variable, valid kwargs and not uncaught raise error"""
    sandbox_api_url = "https://sandbox-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    sandbox_headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c",
    }
    
    run_process(sandbox_api_url, sandbox_headers, mock_universe_file, mock_coins_to_track_file, mock_pricing_data_dir, mock_analysis_save_path)