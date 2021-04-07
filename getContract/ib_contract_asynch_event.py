# -*- coding: utf-8 -*-
"""
IBAPI - Getting Contract info

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self,self)
        
    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId,errorCode,errorString))
        
    def contractDetails(self, reqId, contractDetails):
        print("redID: {}, contract:{}".format(reqId,contractDetails))

def websocket_con():
    app.run()
    event.wait()
    if event.is_set():
        app.close()

event = threading.Event()   
app = TradingApp()      
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con)
con_thread.start()
time.sleep(1) # some latency added to ensure that the connection is established

#creating object of the Contract class - will be used as a parameter for other function calls
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "OPT"
contract.currency = "USD"
contract.exchange = "CBOE"
contract.lastTradeDateOrContractMonth = "20210416"
contract.strike = "200.0"
contract.right = "C"
contract.multiplier = "100"


app.reqContractDetails(100, contract) # EClient function to request contract details

contractstk = Contract()
contractstk.symbol = "AAPL"
contractstk.secType = "STK"
contractstk.currency = "USD"
contractstk.exchange = "SMART"
time.sleep(2)

app.reqContractDetails(200, contractstk)

time.sleep(5) # some latency added to ensure that the contract details request has been processed
event.set()


    