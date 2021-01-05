from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
import time
import threading


class IBapi(EWrapper, EClient):
    # CITATIONS: https://www.quantstart.com/articles/Using-Python-IBPy-and-the-Interactive-Brokers-API-to-Automate-Trades/
    # CITATIONS: https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

    def createOrder(self, order_type, quantity, action):
        # Create order object
        self.order = Order()  # Create order object
        self.order.action = action  # the actionL 'BUY' or 'SELL'
        self.order.totalQuantity = quantity  # Quantity (numshares)
        self.order.orderType = order_type  # 'MKT', 'LMT' for Market or Limit orders

    def createContract(self, shortName, securityType, exchange, primaryExchange, curr):
        """Create a Contract object defining what will
        be purchased, at which exchange and in which currency.

        symbol - The ticker symbol for the contract
        sec_type - The security type for the contract ('STK' is 'stock')
        exch - The exchange to carry out the contract on
        prim_exch - The primary exchange to carry out the contract on
        curr - The currency in which to purchase the contract"""
        # Create contract object
        self.contract = Contract()
        self.contract.symbol = shortName
        self.contract.secType = securityType
        self.contract.exchange = exchange
        self.contract.primaryExch = primaryExchange
        self.contract.currency = curr

    def makeOrder(self):
        self.nextorderId = None
        # Check if the API is connected via orderid
        check = True
        while check:
            if isinstance(self.nextorderId, int):
                print('connected')
                check = False
            else:
                print('waiting for connection')
                time.sleep(1)
        # Place order
        self.placeOrder(self.nextorderId, self.contract, self.order)
        self.nextorderId += 1

    def cancelLatestOrder(self):
        self.cancelOrder(self.nextorderId)


def makeOrder(company, numShares, action):
    def run_loop():
        app.run()

    app = IBapi()
    app.connect('127.0.0.1', 7497, 123)

    app.nextorderId = None

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    app.createOrder(order_type='MKT', quantity=numShares, action=action)

    app.createContract(shortName=company, securityType='STK', exchange='SMART', primaryExchange='SMART', curr='USD')

    # Place order
    app.makeOrder()
    time.sleep(3)

    time.sleep(3)
    app.disconnect()


