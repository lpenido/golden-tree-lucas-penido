# Cryptocurrency Price Tracker

This project is a Python-based cryptocurrency price tracker that integrates with the CoinMarketCap API to analyze the relationship between Bitcoin and other tracked cryptocurrencies. It includes functionality to:

1. Fetch and store the universe of coins in a CSV file.
2. Fetch and store pricing data for specific coins defined in a configuration file.
3. Analyze the relationship between Bitcoin and tracked coins, storing the results in a CSV file.
4. Calculate the average 24-hour percent change difference relative to Bitcoin across multiple runs.

---

## Prerequisites

- Python 3.8+
- A free CoinMarketCap API key. [Get it here](https://coinmarketcap.com/api/pricing/).

---

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:lpenido/golden-tree-lucas-penido.git
   cd golden-tree-lucas-penido
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up a secrets.json file with your API key inside declared as "api_key":
   ```
   {"api_key": "your-api-key"}
   ```

---

## Usage

1. Prepare a `coins_to_track.csv` file with the symbols of coins to track:
   ```csv
   Symbol
   BTC
   ETH
   ```

2. Run the main script with Poetry:
   ```bash
   poetry run python crypto_tracker.py
   ```

   This will:
   - Fetch and save the coin universe in `coin_universe.csv`.
   - Fetch pricing data for the specified coins and save it to the `pricing_data` directory.
   - Analyze Bitcoin's relationship to other coins and save the results to `bitcoin_relationship.csv`.
   - Print average 24-hour percent change differences relative to Bitcoin.

---

## Running Tests

1. Run pytest suite with Pßoetry:
   ```bash
   poetry run pytest
   ```

---

## Project Structure

- `crypto_tracker.py`: Main script with all functionalities.
- `coins_to_track.csv`: Input file specifying the IDs of coins to track.
- `coin_universe.csv`: Output file storing the latest quote information for all coins.
- `pricing_data/`: Directory for storing pricing data CSVs.
- `bitcoin_relationship.csv`: Output file analyzing the relationship between Bitcoin and other coins.
- `tests/`: Directory containing unit tests.

---

## Notes

- Ensure the `coins_to_track.csv` file is correctly formatted with valid CoinMarketCap coin IDs.
- The script automatically appends timestamps to pricing data filenames to avoid overwriting.

---

## Evaluation Criteria

1. Does the process work? Is it resilient? What happens on failures?
    - The process does work and is resilient to most errors. There biggest points of failure I've identified are:
        1. The API is down/unreachable
        2. The API schema changes
        3. There is no BTC data in the API response and nans propogate in analysis
        4. There is no pricing files to iterate over and/or there's no BTC data in pricing data files and nans propogate in analysis
2. Is the process easy to run?
    - The process can be run as a cron schedule, a Task Scheduler job, or built into a CLI tool.
3. Is your code easy to change?
    - The code easy to change because it's composed of decoupled functions. These function are wrapped by run_process which can be tailored to fit changes. Additionally, the run_process configs are stored at the bottom of the file and are easily editable.
4. If you’re on vacation, can your colleagues understand and debug your code?
    - I've provided documentation and a test suite to help any potential colleagues understand and debug my code in my absence.

---