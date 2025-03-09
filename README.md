# Ethereum Key Finder

A multi-threaded Python tool that attempts to find private keys for Ethereum addresses through random generation and matching.

## How It Works

This script reads a CSV file containing Ethereum public keys (addresses) and checks them against randomly generated private keys. Using a ThreadPoolExecutor for parallel processing, it:

1. Loads a list of target Ethereum addresses from a CSV file
2. Generates random private keys in batches
3. Derives the corresponding public address for each private key
4. Checks if any generated address matches one in the target list
5. Saves any matches to a CSV file with the public-private key pair

## Installation

```bash
# Clone the repository
git clone https://github.com/IljaHramcov/eth-key-finder.git

# Navigate to the directory
cd eth-key-finder

# Install dependencies
pip install web3 eth_keys eth_utils
```

## Usage

1. Prepare your CSV file with Ethereum addresses you want to target:
   - Use the provided `top_accounts.csv` with 150k top accounts, or
   - Create your own CSV file with addresses in a single column format

2. Run the script:
   ```bash
   python eth_key_finder_multi.py
   ```

3. If any matches are found, they will be saved to `found_keys.csv`

## Configuration

You can modify these constants in the script to adjust performance:

- `BATCH_SIZE`: Number of keys to generate in each batch (default: 100)
- `MAX_WORKERS`: Number of concurrent threads (default: 12)
- `REPORT_INTERVAL`: How often to log progress (default: every 5000 keys)
- `PUBLIC_KEYS_FILE`: CSV file with target addresses (default: "top_accounts.csv")
- `FOUND_KEYS_FILE`: Output file for matches (default: "found_keys.csv")

## Dependencies

- `web3`: Ethereum interface library
- `eth_keys`: Ethereum key handling
- `eth_utils`: Ethereum utilities including address checksum
- Python standard libraries: csv, time, signal, sys, typing, concurrent.futures, logging, secrets

## Important Note

Finding a matching private key through random generation has an extremely low probability due to the enormous keyspace of Ethereum addresses. This tool is primarily for educational purposes.

## Logs

The script generates logs to both console and a file named `key_finder.log`, showing progress and any matches found.
