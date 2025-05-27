import pandas as pd
from momentum_single_signal import generate_momentum_signals
from montecarlo import lookback_option
def compute_returns(price_data, vol_data, expected_returns_data, start_day=0, lookback=20, waiting=1, holding=5, top_quantile=0.2, bottom_quantile=0.2, long_only=False):
    """
    Generate momentum signals based on past returns.

    Parameters:
    - data: DataFrame with asset prices indexed by date and columns as asset tickers
    - start_day: int, day to start generating signals
    - lookback: int, number of days to calculate momentum
    - waiting: int, delay before entering positions
    - holding: int, how long to hold positions
    - top_quantile: float, quantile threshold for long positions
    - bottom_quantile: float, quantile threshold for short positions
    - long_only: bool, if True only go long
    """

    hold_signals_df = [pd.DataFrame(0, index=price_data.index, columns=price_data.columns)] * len(price_data)
    reverse_signals_df =[pd.DataFrame(0, index=price_data.index, columns=price_data.columns)] * len(price_data)
    option_prices_df = [
        pd.DataFrame(0.0, index=price_data.index, columns=price_data.columns)
        for _ in range(len(price_data))
    ]

    returns_df = [0] * len(price_data)

    for day in range(start_day + lookback, len(price_data) - 2):
        returns = 0
        i = 0
        hold_signals, reverse_signals = generate_momentum_signals(
            price_data,
            start_day=day,
            lookback=lookback,
            waiting=waiting,
            holding=holding,
            top_quantile=top_quantile,
            bottom_quantile=bottom_quantile,
            long_only=long_only
        )
        
        hold_signals_df[day] = hold_signals
        reverse_signals_df[day] = reverse_signals

        # Get the returns from holding
        for d in range(day - holding - waiting, day - waiting):
            returns += (price_data.iloc[d] / price_data.iloc[d - 1] - 1).dot(hold_signals_df[d].iloc[day])
            i+=1
            
        # Get the returns from reversing (option)
        for d in range(day - waiting, day):
            for tick in reverse_signals.columns:
                res = reverse_signals_df[d][tick].iloc[day]
                if res > 0:
                    if option_prices_df[d][tick].iloc[day] == 0:
                        min_price = price_data[tick].iloc[d:day+1].min() # The +1 allows to account for the current day for the realized payoff
                        option_prices_df[d].loc[day, tick] = lookback_option(price_data[tick].iloc[day], vol_data[tick].iloc[day], expected_return=expected_returns_data[tick].iloc[day], rate=0.03,time=(res-1)/252, min_price=min_price, dt=1/252, nb_paths=1000, fee= 0.05)
                        
                    if option_prices_df[d][tick].iloc[day - 1] == 0:
                        min_price = price_data[tick].iloc[d:day].min() # The +1 allows to account for the current day for the realized payoff. it its cancelled by the -1
                        option_prices_df[d].loc[day - 1, tick] = lookback_option(price_data[tick].iloc[day - 1], vol_data[tick].iloc[day - 1], expected_return=expected_returns_data[tick].iloc[day - 1], rate=0.03,time=(res)/252, min_price=min_price, dt=1/252, nb_paths=1000, fee= 0.05)
                        
                    # If we allocate $1000 to every allocation, then we should buy 1000/S0 options
                    S = price_data[tick].iloc[d]
                    returns += (option_prices_df[d][tick].iloc[day] + S - S/1000 * option_prices_df[d][tick].iloc[d]) / (option_prices_df[d][tick].iloc[day - 1] + S - S/1000 * option_prices_df[d][tick].iloc[d]) - 1
                    i+=1
        
        if i > 0:
            returns_df[day] = returns / i

        for j in range(0,day-lookback-waiting-10):
            hold_signals_df[j] = None
            reverse_signals_df[j] = None
    
    return returns_df


    