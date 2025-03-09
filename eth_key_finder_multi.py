import csv
import time
import signal
import sys
from typing import Set, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from web3 import Web3
from eth_keys import keys
from eth_utils import to_checksum_address
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("key_finder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BATCH_SIZE = 100
MAX_WORKERS = 12
REPORT_INTERVAL = 5000
PUBLIC_KEYS_FILE = "top_accounts.csv"
FOUND_KEYS_FILE = "found_keys.csv"

def read_public_keys(file_path: str) -> Set[str]:
    """Read public keys from a CSV file"""
    public_keys = set()
    try:
        with open(file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if row:
                    public_keys.add(row[0].lower())
        logger.info(f"Loaded {len(public_keys)} public keys from {file_path}")
        return public_keys
    except Exception as e:
        logger.error(f"Error reading public keys: {e}")
        sys.exit(1)

def generate_and_check_keys(public_keys: Set[str], batch_size: int) -> List[Tuple[str, str]]:
    """Generate and check keys against public keys set"""
    matches = []
    for _ in range(batch_size):
        # Generate random private key
        private_key_bytes = secrets.token_bytes(32)
        private_key_hex = private_key_bytes.hex()
        
        # Get public key (address)
        private_key = keys.PrivateKey(private_key_bytes)
        public_key = private_key.public_key
        address = public_key.to_address()
        
        # Check if address is in our target set
        if address.lower() in public_keys:
            matches.append((address.lower(), private_key_hex))
            
    return matches

def save_found_keys(matches: List[Tuple[str, str]]) -> None:
    """Save found keys to CSV file"""
    if not matches:
        return
        
    try:
        with open(FOUND_KEYS_FILE, 'a', newline='') as found_keys_file:
            csv_writer = csv.writer(found_keys_file)
            for public_key, private_key in matches:
                csv_writer.writerow([public_key, private_key])
                logger.info(f"MATCH FOUND! Public key: {public_key}")
    except Exception as e:
        logger.error(f"Error saving found keys: {e}")

def main():
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down gracefully...")
        if executor:
            executor.shutdown(wait=False)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load public keys
    public_keys = read_public_keys(PUBLIC_KEYS_FILE)
    if not public_keys:
        logger.error("No public keys loaded. Exiting.")
        return
    
    # Initialize counters and timer
    start_time = time.time()
    keys_checked = 0
    last_report_time = start_time
    found_keys_count = 0
    
    # Create executor
    logger.info(f"Starting search with {MAX_WORKERS} workers")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = set()
        
        # Submit initial batch of tasks
        for _ in range(MAX_WORKERS):
            future = executor.submit(generate_and_check_keys, public_keys, BATCH_SIZE)
            futures.add(future)
        
        # Process results as they complete
        try:
            while futures:
                # Process completed futures
                completed_futures = set()
                for future in as_completed(futures, timeout=10):
                    completed_futures.add(future)
                    try:
                        matches = future.result()
                        keys_checked += BATCH_SIZE
                        
                        # Handle any matches
                        if matches:
                            found_keys_count += len(matches)
                            save_found_keys(matches)
                        
                        # Report progress periodically
                        if keys_checked % REPORT_INTERVAL == 0:
                            current_time = time.time()
                            elapsed_total = current_time - start_time
                            elapsed_since_last = current_time - last_report_time
                            keys_per_second = REPORT_INTERVAL / elapsed_since_last if elapsed_since_last > 0 else 0
                            
                            logger.info(
                                f"Checked {keys_checked:,} keys in {elapsed_total:.1f}s "
                                f"({keys_per_second:.1f} keys/sec, {found_keys_count} matches found)"
                            )
                            last_report_time = current_time
                            
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}")
                
                # Remove completed futures and submit new tasks
                for completed in completed_futures:
                    futures.remove(completed)
                    future = executor.submit(generate_and_check_keys, public_keys, BATCH_SIZE)
                    futures.add(future)
                            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
        finally:
            executor.shutdown(wait=False)
            
    # Final statistics
    total_time = time.time() - start_time
    logger.info(f"Search completed. Checked {keys_checked:,} keys in {total_time:.1f}s")
    logger.info(f"Average speed: {keys_checked/total_time:.1f} keys/sec")
    logger.info(f"Total matches found: {found_keys_count}")

if __name__ == "__main__":
    main()
