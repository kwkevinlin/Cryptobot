# Cryptobot
This is an on-going project to create a useful bot to track your personal cryptocurrency portfolios.

**Exchanges supported:** Coinbase  
**Info needed:** API key 

### Current features:
- List all transactions by coin
- Calculate profit/loss for each coin (value in USD, % change)
- Calculate profit/loss for entire portfolio
- Supports multiple accounts within Coinbase and allows manual input of external balances

### Future features:
- Support other exchanges (Bittrex, Kraken)
- Automate external balance import from other exchanges/Coinigy

### Installation steps:
1. These steps assume python3 and pip3 are already installed
3. Install the official Coinbase Python SDK `sudo pip3 install coinbase`
3. In Coinbase, navigate to **Settings** -> **API Access** -> **New API Key** to generate a new set of API credentials
4. Select the accounts you wish the bot to be able to operate on
5. Select all API read permissions
6. ***Note:** This bot does not require buy, sell, or transfer permissions*
    <img src="https://raw.githubusercontent.com/kwkevinlin/Cryptobot/master/images/coinbase_permissions.jpg" height="536" width="490">
5. Enter API information from step 3 into `config.json`
6. Remember to keep the API key safe as the key will no longer be visible on Coinbase
7. Run Cryptobot via `python3 cryptobot.py -u user -e 300 -v` (see run configurations below)

### Run configurations:
Cryptobot takes the following command line arguments
- `-u, --user`: Specifies the credential set in `config.json` to use
- `-e, --ethereum`: Sets the current ethereum price for profit calculations (Coinbase SDK does not return this value correctly)
- `-v, --verbose`: Extra printout on transaction details
