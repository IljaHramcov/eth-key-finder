# Ethereum Key Finder

This script reads a CSV file containing public keys and checks them against randomly generated private keys using a ThreadPoolExecutor. If a match is found between a public key in the CSV file and the public key derived from a randomly generated private key, the script writes the matching public key and private key to a new CSV file.

##Usage
+ Clone the repository: git clone https://github.com/IljaHramcov/eth-key-finder.git
+ Use the given CSV file with 150k top accounts. Or create a CSV file containing the public keys you want to match in the format of a single column.
+ Run the script.

##Dependencies
This script uses the following dependencies:

+ eth_account
