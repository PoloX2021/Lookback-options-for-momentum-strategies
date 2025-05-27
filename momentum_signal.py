import pandas as pd
import numpy as np

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
    Generate signals that rebalance every 'holding' days and remain constant in between.
    """
    data = data.sort_values(['ticker', 'day']).copy()
    data['momentum_return'] = data.groupby('ticker')['price'].pct_change(periods=lookback)
    data['momentum_return'] = data.groupby('ticker')['momentum_return'].shift(waiting)

    # Drop missing values from return calculation
    data = data.dropna(subset=['momentum_return'])

    # Extract unique dates and choose rebalancing days
    trading_days = sorted(data['day'].unique())
    rebalance_days = trading_days[::holding]

    # Filter to rebalance days
    rebalance_data = data[data['day'].isin(rebalance_days)]

    # Assign signals on rebalance days
    def assign_signals(group):
        q_low = group['momentum_return'].quantile(bottom_quantile)
        q_high = group['momentum_return'].quantile(1 - top_quantile)
        group['signal'] = 0
        group.loc[group['momentum_return'] >= q_high, 'signal'] = 1
        if not long_only:
            group.loc[group['momentum_return'] <= q_low, 'signal'] = -1
        return group

    rebalance_signals = rebalance_data.groupby('day').apply(assign_signals).reset_index(drop=True)
    print(rebalance_signals.head(30))

    # Propagate signals forward for the entire holding period
    signal_list = []
    reverse_signal_list = []

    for i, day in enumerate(rebalance_days):
        # Get signal for this rebalance day
        temp = rebalance_signals[rebalance_signals['day'] == day].copy()

        # Get index of current rebalance day
        start_idx = trading_days.index(day)

        # 1. Tag waiting period (before rebalance)
        if waiting > 0 and start_idx - waiting >= 0:
            waiting_days = trading_days[start_idx - waiting:start_idx]
            wait_temp = temp.loc[temp.index.repeat(len(waiting_days))]
            wait_temp['day'] = np.tile(waiting_days, len(temp))
            wait_temp['signal'] = wait_temp['signal'].map(lambda x: 1 if x == 1 else (-1 if x == -1 else 0))
            reverse_signal_list.append(wait_temp)

        # 2. Apply actual signal for holding period
        end_idx = min(start_idx + holding - waiting, len(trading_days))
        holding_days = trading_days[start_idx:end_idx]

        hold_temp = temp.loc[temp.index.repeat(len(holding_days))]
        hold_temp['day'] = np.tile(holding_days, len(temp))
        signal_list.append(hold_temp)

    held_signals = pd.concat(signal_list)
    held_signals = held_signals.groupby(['day', 'ticker'])['signal'].mean().reset_index()

    reverse_signals = pd.concat(reverse_signal_list)
    reverse_signals = reverse_signals.groupby(['day', 'ticker'])['signal'].mean().reset_index()

    return held_signals, reverse_signals
