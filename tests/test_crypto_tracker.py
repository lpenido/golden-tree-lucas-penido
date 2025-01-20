from pathlib import Path
import os
from unittest.mock import patch, Mock

import pytest
import pandas as pd

from crypto_tracker import (
    get_coin_universe,
    get_coins_to_track,
    PRICING_DATA_DIR,
    COINS_TO_TRACK_FILE     
)


@pytest.fixture
def mock_coin_universe_response():
    return {
        "data": [
            {"id": 1, "name": "Bitcoin", "symbol": "BTC", "slug": "bitcoin", "num_market_pairs": 11869, "date_added": "2010-07-13T00:00:00.000Z", "tags": ["mineable", "pow", "sha-256", "store-of-value", "state-channel", "coinbase-ventures-portfolio", "three-arrows-capital-portfolio", "polychain-capital-portfolio", "binance-labs-portfolio", "blockchain-capital-portfolio", "boostvc-portfolio", "cms-holdings-portfolio", "dcg-portfolio", "dragonfly-capital-portfolio", "electric-capital-portfolio", "fabric-ventures-portfolio", "framework-ventures-portfolio", "galaxy-digital-portfolio", "huobi-capital-portfolio", "alameda-research-portfolio", "a16z-portfolio", "1confirmation-portfolio", "winklevoss-capital-portfolio", "usv-portfolio", "placeholder-ventures-portfolio", "pantera-capital-portfolio", "multicoin-capital-portfolio", "paradigm-portfolio", "bitcoin-ecosystem", "ftx-bankruptcy-estate", "2017-2018-alt-season"], "max_supply": 21000000, "circulating_supply": 19812890, "total_supply": 19812890, "infinite_supply": False, "platform": None, "cmc_rank": 1, "self_reported_circulating_supply": None, "self_reported_market_cap": None, "tvl_ratio": None, "last_updated": "2025-01-20T23:01:00.000Z", "quote": {"USD": {"price": 103325.80885486708, "volume_24h": 133037548480.13788, "volume_change_24h": 93.7051, "percent_change_1h": 1.02022321, "percent_change_24h": 0.69860286, "percent_change_7d": 9.67106845, "percent_change_30d": 6.4215294, "percent_change_60d": 4.92526738, "percent_change_90d": 52.55814934, "market_cap": 2047182885002.5073, "market_cap_dominance": 57.2814, "fully_diluted_market_cap": 2169841985952.21, "tvl": None, "last_updated": "2025-01-20T23:01:00.000Z"}}},
            {"id": 1027, "name": "Ethereum", "symbol": "ETH", "slug": "ethereum", "num_market_pairs": 9842, "date_added": "2015-08-07T00:00:00.000Z", "tags": ["pos", "smart-contracts", "ethereum-ecosystem", "coinbase-ventures-portfolio", "three-arrows-capital-portfolio", "polychain-capital-portfolio", "heco-ecosystem", "binance-labs-portfolio", "avalanche-ecosystem", "solana-ecosystem", "blockchain-capital-portfolio", "boostvc-portfolio", "cms-holdings-portfolio", "dcg-portfolio", "dragonfly-capital-portfolio", "electric-capital-portfolio", "fabric-ventures-portfolio", "framework-ventures-portfolio", "hashkey-capital-portfolio", "kenetic-capital-portfolio", "huobi-capital-portfolio", "alameda-research-portfolio", "a16z-portfolio", "1confirmation-portfolio", "winklevoss-capital-portfolio", "usv-portfolio", "placeholder-ventures-portfolio", "pantera-capital-portfolio", "multicoin-capital-portfolio", "paradigm-portfolio", "tezos-ecosystem", "near-protocol-ecosystem", "bnb-chain-ecosystem", "velas-ecosystem", "ethereum-pow-ecosystem", "osmosis-ecosystem", "layer-1", "ftx-bankruptcy-estate", "zksync-era-ecosystem", "viction-ecosystem", "klaytn-ecosystem", "sora-ecosystem", "rsk-rbtc-ecosystem", "starknet-ecosystem"], "max_supply": None, "circulating_supply": 120501725.21190895, "total_supply": 120501725.21190895, "infinite_supply": True, "platform": None, "cmc_rank": 2, "self_reported_circulating_supply": None, "self_reported_market_cap": None, "tvl_ratio": None, "last_updated": "2025-01-20T23:02:00.000Z", "quote": {"USD": {"price": 3305.290787681842, "volume_24h": 55416687850.433754, "volume_change_24h": 2.1574, "percent_change_1h": 0.94068359, "percent_change_24h": 2.58135749, "percent_change_7d": 5.71785649, "percent_change_30d": -0.65987165, "percent_change_60d": -1.93840292, "percent_change_90d": 25.34849309, "market_cap": 398293242242.69147, "market_cap_dominance": 11.1404, "fully_diluted_market_cap": 398293242242.69, "tvl": None, "last_updated": "2025-01-20T23:02:00.000Z"}}}
        ]
    }

@pytest.fixture
def mock_universe_file():
    test_universe_file = Path("test_coin_universe.csv")
    yield test_universe_file
    test_universe_file.unlink(missing_ok=True)

def test_pricing_data_directory():
    """The directory for pricing data should exist"""
    assert PRICING_DATA_DIR.exists() == True


@patch("crypto_tracker.requests.get")
def test_get_coin_universe(mock_get, mock_coin_universe_response, mock_universe_file):
    """Testing the schema saves"""
    mock_get.return_value = Mock(status_code=200, json=lambda: mock_coin_universe_response)

    get_coin_universe(mock_universe_file)

    assert mock_universe_file.exists() == True
    df = pd.read_csv(mock_universe_file)
    assert len(df) == 2
    primary_columns = ["name", "symbol", "percent_change_24h"]
    assert all(col in df.columns for col in primary_columns)
    assert "BTC" in df["symbol"].values
    assert "ETH" in df["symbol"].values

def test_get_coins_to_track():
    """Making sure the file to track coins exists and has at least BTC in it"""
    coins_to_track = get_coins_to_track()
    assert len(coins_to_track) > 0
    assert "BTC" in coins_to_track
