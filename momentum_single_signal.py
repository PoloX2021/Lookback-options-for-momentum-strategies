import pandas as pd

def generate_momentum_signals(
    data,
    start_day,
    lookback=20,
    waiting=1,
    holding=5,
    top_quantile=0.2,
    bottom_quantile=0.2,
    long_only=False
):
    """
    Generate momentum-based signals at a specific start date.

    Parameters:
    - data: DataFrame of prices (rows: dates, columns: tickers)
    - start_day: int, day index to calculate momentum and begin waiting period
    - lookback: int, number of days to calculate momentum
    - waiting: int, delay before entering positions
    - holding: int, how long to hold positions
    - top_quantile: float, quantile threshold for long positions
    - bottom_quantile: float, quantile threshold for short positions
    - long_only: bool, if True only go long

    Returns:
    - signals: DataFrame with +1 (long), -1 (short), or 0 for each day and asset
    """

    hold_signals = pd.DataFrame(0, index=data.index, columns=data.columns)
    reverse_signals = pd.DataFrame(0, index=data.index, columns=data.columns)

    # Check bounds
    if start_day < lookback:
        raise ValueError("Invalid start_day, lookback, waiting, or holding period for given data length.")

    # Momentum: return over lookback window
    past_returns = data.iloc[start_day] / data.iloc[start_day - lookback] - 1
    past_returns = past_returns.dropna()

    # Select long and short candidates
    long_thresh = past_returns.quantile(1 - top_quantile)
    long_candidates = past_returns[past_returns >= long_thresh].index

    short_candidates = []
    if not long_only:
        short_thresh = past_returns.quantile(bottom_quantile)
        short_candidates = past_returns[past_returns <= short_thresh].index

    # Define the holding period window
    start_day = start_day + 1
    entry_day = start_day + waiting
    exit_day = entry_day + holding

    # Assign signals
    if exit_day <= len(data):
        hold_signals.loc[data.index[entry_day:exit_day], long_candidates] = 1
        if not long_only:
            hold_signals.loc[data.index[entry_day:exit_day], short_candidates] = -1

        for i in range(waiting):
            day = start_day + i
            value = waiting - i
            reverse_signals.loc[data.index[day], long_candidates] = value
        if not long_only:
            for i in range(waiting):
                day = start_day + i
                value = waiting - i
                reverse_signals.loc[data.index[day], short_candidates] = - value
    
    elif entry_day < len(data):
        hold_signals.loc[data.index[entry_day:], long_candidates] = 1
        if not long_only:
            hold_signals.loc[data.index[entry_day:], short_candidates] = -1
        
        for i in range(waiting):
            day = start_day + i
            value = waiting - i
            reverse_signals.loc[data.index[day], long_candidates] = value
        if not long_only:
            for i in range(waiting):
                day = start_day + i
                value = waiting - i
                reverse_signals.loc[data.index[day], short_candidates] = - value
    
    else:
        for i in range(len(data) - start_day):
            day = start_day + i
            value = waiting - i
            reverse_signals.loc[data.index[day], short_candidates] = value
        if not long_only:
            for i in range(len(data) - start_day):
                day = start_day + i
                value = waiting - i
                reverse_signals.loc[data.index[day], short_candidates] = - value
    
    return hold_signals, reverse_signals
