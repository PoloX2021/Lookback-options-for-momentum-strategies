We try to measure the impact of lookback options to take advantage of the mean reverse that generally happens before a stock grows in momentum.

montecarlo.py simulates the price of a lookback option. By default we add a 5% premium paid to the issuer.
momentum_single_signal.py computes the momentum indicators at one given time
simulate_returns.py aggregates signals to get the daily returns

Tests:
test_data.py generates random stock prices to use in test.py which simulates the behavior of the above functions.