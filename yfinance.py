import yfinance as yf


@bot.message_handler(commands=["ssb"])  # "Satoshi Street Bets|
def get_crypto_data(message):
    response = ""
    crypto = ["BTC", "ETH", "XRP", "TRX"]
    crypto_data = []
    for crypto in cryptos:
        data = yf.dowload(ticker=crypto, period="1d", interval="1d")
        data = data.reset_index()
        response += f"{crypto}: {data['Close'][0]}\n"
        crypto_data.append([crypto, data["Close"][0]])
        columns = ["crypto", "price"]
        for index, row in data.iterrows():
            # Add logic here to send alerts
            pass

    bot.reply_to(message, response)  # Send the response to the user
