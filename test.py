import pandas as pd
from momentum_single_signal import generate_momentum_signals
from simulate_returns import compute_returns
from test_data import generate_sample_data
from time import time


def test_signal():
    sample_data = pd.read_excel('sample_data.xlsx')

    sample_data['day'] = pd.to_datetime(sample_data['date'])
    sample_data['ticker'] = sample_data['TICKER']
    sample_data['price'] = (sample_data['BID'] + sample_data['ASK']) / 2

    sample_data = sample_data[['day', 'ticker', 'price']]

    price_data = sample_data.pivot(index='day', columns='ticker', values='price').sort_index()
    price_data.index = range(len(price_data))
    print(price_data.head(10))

    res1, res2 = generate_momentum_signals(price_data, start_day=6, lookback=5, waiting=2)

    print(res1.head(15))
    print(res2.head(15))


    """hold, reverse = generate_momentum_signals(sample_data, lookback=20, waiting=1, holding=5, top_quantile=0.2, bottom_quantile=0.2, long_only=False)
    print(hold[hold['ticker']=='AAPL'].head(40))
    print(reverse[reverse['ticker']=='AAPL'].head(40))"""

#test_signal()

def test_returns():
    t = time()
    price_df, vol_df, expected_returns_df = generate_sample_data()
    print(price_df.head(len(price_df)))

    returns = compute_returns(
        price_data=price_df,
        vol_data=vol_df,
        expected_returns_data=expected_returns_df,
        start_day=0,
        lookback=5,
        waiting=2,
        holding=3,
        top_quantile=0.2,
        bottom_quantile=0.2,
        long_only=True
    )

    print(returns)
    print(f"Time taken: {time() - t:.2f} seconds")

test_returns()