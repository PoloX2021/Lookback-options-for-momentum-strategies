import pandas as pd
import numpy as np


def generate_sample_data():
    expected_returns = 0.02
    volatility = 0.2
    i = 1
    days = 13 * i
    tickers = []
    n = 1
    print(i,n)
    temp = ''
    for i in range(n):
        temp+='A'
        tickers.append(temp)


    price_df = pd.DataFrame(0, index=range(days), columns=tickers)
    for ticker in tickers:
        price = 100  # Starting price
        prices = [price]
        for day in range(1, days):
            daily_return = np.random.normal(expected_returns / days, volatility / np.sqrt(days))
            price *= (1 + daily_return)
            prices.append(price)
        price_df[ticker] = prices

    vol_df = pd.DataFrame(volatility, index=range(days), columns=tickers)

    expected_returns_df = pd.DataFrame(expected_returns, index=range(days), columns=tickers)

    return price_df, vol_df, expected_returns_df
