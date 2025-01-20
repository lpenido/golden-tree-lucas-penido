from crypto_tracker import (
    PRICING_DATA_DIR
)

def test_pricing_data_directory():
    """The directory for pricing data should exist"""
    assert PRICING_DATA_DIR.exists() == True
