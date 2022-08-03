from web3 import Web3
from hashlib import sha256
import json
import requests as r

url = 'http://127.0.0.1:7545'

web3 = Web3(Web3.HTTPProvider(url))

def SHA256(text):
    return sha256(text.encode("ascii")).hexdigest()

#gas = 2000000

def make_transaction(account_sender, account_reciver, private_key, value, gas):
    nonce = web3.eth.get_transaction_count(account_sender)

    transaction_tx = {
        'nonce' : nonce,
        'to': account_reciver,
        'value': web3.toWei(value, 'ether'),
        'gas': gas,
        'gasPrice': web3.toWei(50, 'gwei')
    } 

    signed_tx = web3.eth.account.sign_transaction(transaction_tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.toHex(tx_hash)


def get_val_eth(value):
    x = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    y = r.get(x).json()
    ether_price = y[1]
    if value:
        price = value/float(ether_price['current_price'])
        return price
    else:
        return float(ether_price['current_price'])



def get_acc_bal(account):
    balance = web3.eth.getBalance(account)
    balance = web3.fromWei(balance, 'ether')
    return balance


if __name__ == '__main__':
    # print(make_transaction(account_sender = '0x9Fb3e365D6bA2fDf0afe9E2Eb04202bd30d04Fb9',
    #                        account_reciver = '0x1a26b4cFbCC3Dd5D0E34e69d3c33e5DA46BA7450',
    #                        private_key = 'e53c9eb749069861af19a18c49a0db167a65e9b78920d9dd5124c96c7fda6ec1',
    #                        value = 0.09,
    #                        gas = 200000,))
    print('Yes')