import csv
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from eth_account import Account

def read_public_keys(file: str) -> Dict[str, bool]:
    """
    Read public keys from a CSV file and return them in a dictionary
    """
    public_keys = {}
    with open(file, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            public_keys[row[0].lower()] = True
    return public_keys

# Create a dictionary with public keys from the public_keys.csv file
public_keys = read_public_keys("top_accounts.csv")

# Create a ThreadPoolExecutor with a specified number of threads
executor = ThreadPoolExecutor(max_workers=4)

futures = set()

#  Keep generating private keys and checking them until a match is found
while True:
    # Submit a task to the executor to generate a private key and check it against the CSV file
    future = executor.submit(Account.create)
    futures.add(future)

    for future in as_completed(futures):
        private_key = future.result().privateKey
        public_key = Account.privateKeyToAccount(private_key).address.lower()
        if public_key in public_keys:
            print(f'Public key {public_key} found in CSV file')
            with open('found_keys.csv', 'a') as found_keys_file:
                csv_writer = csv.writer(found_keys_file)
                csv_writer.writerow([public_key, private_key.hex()])
            # Close the file after each iteration
            found_keys_file.close()
            futures.remove(future)
            break
        else:
            #print(f'Public key {public_key} not found in CSV file')
            futures.remove(future)
