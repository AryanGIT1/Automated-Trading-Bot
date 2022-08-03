import requests as r
import time
import json

def main(ad):
    while True:
        x = 'http://127.0.0.1:5000/api/algo/trade/'+ str(ad) + '/'
        print(x)
        y = r.get(x)
        print(y.status_code, y)
        time.sleep(5)
    
    # x = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'
    # y = r.get(x).json()
    # ether_price = y[1]
    # print(ether_price['current_price'])
        
    # x = 'http://127.0.0.1:5000/api/info/user/'+ str(ad)
    # print(x)
    # y = r.get(x)
    # print(y.status_code, y)
    # time.sleep(5)
    
    

if __name__ == '__main__':
    x = '0xec5766aB31a5Ca14C5968b4fD3d91e0b55659528'
    main(x)