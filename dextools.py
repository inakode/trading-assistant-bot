# -*- coding: utf-8 -*-
# PULLS DATA FORM DEX TOOLS API

import json
import websocket
import axios from 'axios'

from dextools_python import DextoolsAPIV2

dextools = DextoolsAPIV2(api_key, plan="standard")

blockchain = dextools.get_blockchain("ether")
print(blockchain)

token_price = dextools.get_token_price("ether", "0xfb7b4564402e5500db5bb6d63ae671302777c75a")
print(token_price)

token_info = dextools.get_token_info("ether", "0xfb7b4564402e5500db5bb6d63ae671302777c75a")
print(token_info)

dexes = dextools.get_dexes("ether")
print(dexes)

blockchains = dextools.get_blockchains(sort="name", order="desc")
print(blockchains)



asset = ['ETHUSDT', 'BTCUSDT', 'BNBUSDT']

def get_dextools_data(ticker: str, period: str = "1d", interval: str = "1d") -> dict:
    """
    Get data for a given ticker from Dextools.

    Parameters
    ----------
    ticker : str
        Crypto ticker symbol.
    period : str, optional
        Data period. Defaults to "1d".
    interval : str, optional
        Data interval. Defaults to "1d".
    """
    url = f"https://api.dextools.io/api/{ticker}"
    headers = {'Authorization': f'Bearer {dextools_api_key}'}
    params = {'period': period, 'interval': interval}
    response = requests.get(url, headers=headers, params=params)
    return response.json()
    