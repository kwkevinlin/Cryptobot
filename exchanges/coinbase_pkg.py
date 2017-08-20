from coinbase.wallet.client import Client
from pprint import pprint
# TODO instead of hardcoding BTC and ETH formulas separately, use API .account to simplify code


class Coinbase:
    def __init__(self, config, user, verbose):
        # TODO: Add JSON schema validation to main.py
        api_key = config[user]["coinbase_api"][key]
        api_secret = config[user]["coinbase_api"][secret]

        self.client = Client(api_key, api_secret)

        self.verbose = verbose

        # Initialize all calculated numbers
        self.accumulated_profit_btc = 0
        self.accumulated_profit_eth = 0
        self.total_btc_paid_fees = 0
        self.total_eth_paid_fees = 0
        self.total_btc_received = 0
        self.total_eth_received = 0

    def set_eth_price(self, price):
        """ TODO automatically update ETH price, Coinbase API error
        """
        self.current_eth_price = price

    def get_exchange_rate(self, coin="BTC", currency="USD"):
        """ Get BTC - USD exchange rate
            Bug for ETH-USD:
            https://community.coinbase.com/t/python-3-5-get-spot-price-for-eth-eur-returns-btc-usd/14273/9
            Modify source library code:
            https://stackoverflow.com/a/23075617/3751589
        """
        param = "{}-{}".format(coin, currency)
        return self.client.get_spot_price(currency_pair=param)

    def calculate_profit_loss(self):
        self.current_btc_price = float(self.get_exchange_rate("BTC", "USD").amount)
        # self.current_eth_price = float(self.get_exchange_rate("ETH", "USD").amount)

        # Ask user for balance outside of Coinbase
        BTC_external_balance = float(input('BTC external balance: '))
        ETH_external_balance = float(input('ETH external balance: '))

        # Get all accounts listing
        accounts = self._get_accounts()
        print("Accounts retrieved: {}\n".format(len(accounts.data)))

        # Read each account
        for account in accounts.data:
            currency = account.balance.currency
            if currency in ("USD", "LTC") or account.name == "My Vault":  # Ignore these accounts
                # TODO add USD wallet
                continue
            print(currency)

            print("Calculating currency: {}".format(currency))
            print("{}: {} {}".format(account.name, account.balance.amount, currency))

            # Get all transactions
            transactions = account.get_transactions(start_after="1805ae5b-f65b-5825-b780-9c6cecdec1cf", limit=100)
            """ Documentation for argument syntax in get_transactions
                https://github.com/coinbase/coinbase-python/blob/f9ed2249865c2012e3b86106dad5f8c6068366ed/coinbase/wallet/model.py#L168
            """
            # TODO regex or some way to find everyones start_after
            # https://stackoverflow.com/questions/44351034/pagination-on-coinbase-python-api
            for transaction in transactions.data:
                if transaction.status != "completed":
                        print("\tIncomplete transaction...")
                        continue

            # Calculate for each transaction type
                # Calculate all BUYS
                if transaction.type == "buy":
                    transaction_id = transaction.buy.id
                    transaction_detail = self._get_buy_transaction(account.id,
                                                                   transaction_id)

                    # Calculate price point during purchase
                    amount_paid = float(transaction_detail.subtotal.amount)  # USD paid before fees
                    coins_bought = float(transaction_detail.amount.amount)  # Total coins received from purchase
                    purchase_price = amount_paid / coins_bought  # Price of BTC/ETH at time of buying
                    amount_paid_fees = float(transaction.native_amount.amount)  # USD paid after fees (total paid)

                    # Turn into dict
                    # self.total_paid_fees = {}

                    # Calculate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc -= amount_paid_fees
                        self.total_btc_paid_fees += amount_paid_fees
                        # self.total_paid_fees[currency]
                    elif currency == "ETH":
                        self.accumulated_profit_eth -= amount_paid_fees
                        self.total_eth_paid_fees += amount_paid_fees

                    if (self.verbose):
                        print("\tBuy transaction: -{}".format(amount_paid_fees))

                # Calculate all SELLS
                elif transaction.type in ("sell"):
                    # Amount received after fees
                    amount_received = float(transaction.native_amount.amount)
                    amount_received = amount_received * -1

                    # Accumulate profit-loss
                    if currency == "BTC":
                        self.accumulated_profit_btc += amount_received
                        self.total_btc_received += amount_received
                    elif currency == "ETH":
                        self.accumulated_profit_eth += amount_received
                        self.total_eth_received += amount_received

                    if (self.verbose):
                        print("\t{} transaction: {}".format(transaction.type.title(), amount_received))

            # Add current Coinbase balance + current external balance to profit/Loss
            if currency == "BTC":
                # BTC_external_value = BTC_external_balance * self.btc_current_price
                account.balance.amount = float(account.balance.amount)
                self.accumulated_profit_btc += (BTC_external_balance + account.balance.amount) * self.current_btc_price
                self.percent_profit_btc = self.accumulated_profit_btc / self.total_btc_paid_fees
                self.total_btc_balance = (BTC_external_balance + account.balance.amount) * self.current_btc_price
            elif currency == "ETH":
                # ETH_external_value = ETH_external_balance * self.eth_current_price
                account.balance.amount = float(account.balance.amount)
                self.accumulated_profit_eth += (ETH_external_balance + account.balance.amount) * self.current_eth_price
                self.percent_profit_eth = self.accumulated_profit_eth / self.total_eth_paid_fees
                self.total_eth_balance = (ETH_external_balance + account.balance.amount) * self.current_eth_price
            # Print accumulated profit/loss
            if currency == "BTC":
                print("\nProfit/Loss ({}): ${:.2f} or {:.2f}%".format(currency, self.accumulated_profit_btc, (self.percent_profit_btc * 100)))
            elif currency == "ETH":
                print("\nProfit/Loss ({}): ${:.2f} or {:.2f}%\n".format(currency, self.accumulated_profit_eth, (self.percent_profit_eth * 100)))

        # Print balance start --> balance now
        self.total_accumulated_profit = self.accumulated_profit_btc + self.accumulated_profit_eth
        self.total_paid_fees = self.total_btc_paid_fees + self.total_eth_paid_fees
        self.total_acc_balance = self.total_btc_balance + self.total_eth_balance + self.total_eth_received + self.total_btc_received
        print("\nTotal USD Value (ALL): ${:.2f} --> ${:.2f}".format(self.total_paid_fees, self.total_acc_balance))

        # Print total account (BTC + ETH) profit/loss
        self.percent_profit_total = (self.accumulated_profit_btc + self.accumulated_profit_eth) / (self.total_eth_paid_fees + self.total_btc_paid_fees) * 100
        print("Profit/Loss (ALL): ${:.2f} or {:.2f}%\n".format(self.accumulated_profit_btc + self.accumulated_profit_eth, self.percent_profit_total))

    def _get_accounts(self):
        return self.client.get_accounts()

    def _get_buy_transaction(self, account_id, transaction_id):
        return self.client.get_buy(account_id,
                                   transaction_id)
