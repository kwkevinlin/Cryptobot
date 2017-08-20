import json
import argparse
from pprint import pprint
from exchanges.coinbase_pkg import Coinbase


def get_config():
    with open("config.json") as f:
        return json.load(f)


def validate_input(config, user):
    if user not in config:
        raise ValueError("User not defined in config")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user',
                        help='Specify user to process, defined in config file')
    parser.add_argument('-e', '--ethereum',
                        type=int,
                        help='Enter current ethereum price, interim solution for Coinbase API issue')
    parser.add_argument('-v', '--verbose',
                        action='store_true', default=False,
                        help='Debug mode')
    args = parser.parse_args()
    user = args.user
    eth_price = args.ethereum
    verbose = args.verbose

    config = get_config()
    validate_input(config, user)

    # Coinbase
    coinbase = Coinbase(config, user, verbose)
    coinbase.set_eth_price(eth_price)
    coinbase.calculate_profit_loss()


if __name__ == "__main__":
    main()
