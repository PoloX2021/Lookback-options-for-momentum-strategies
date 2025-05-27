import numpy as np
import matplotlib.pyplot as plt
import time as t

def lookback_option(price, volatility, expected_return, rate, time, min_price = 10**10, dt = 1/252, nb_paths = 10000, fee = 0.05, plot = False):
    """
    Prices a European lookback option using Monte Carlo simulation.
    
    Parameters:
    - price: Initial asset price (float)
    - strike: Strike price of the option (float)
    - volatility: Volatility of the underlying asset (float, annualized)
    - expected_return: Expected return of the asset (float, annualized)
    - rate: Risk-free interest rate (float, annualized)
    - time: Time to maturity in years (float)
    - resolution: Number of simulated price paths (int)
    
    Returns:
    - Estimated option price (float)
    """
    steps = int(time / dt)  # Number of time steps
    
    # Precompute constants
    drift = (expected_return - 0.5 * volatility**2) * dt
    diffusion = volatility * np.sqrt(dt)

    # Simulate random price paths (resolution x steps)
    rand_matrix = np.random.randn(nb_paths, steps)
    price_paths = price * np.exp(np.cumsum(drift + diffusion * rand_matrix, axis=1))
    if plot is True:
        for i in range(nb_paths):
            plt.plot(price_paths[i], label=f'Path {i+1}')
        plt.title('Simulated Price Paths')
        plt.xlabel('Time Steps')
        plt.ylabel('Price')
        plt.show()

    # Include initial price in path
    price_paths = np.concatenate([np.full((nb_paths, 1), price), price_paths], axis=1)

    # Floating-strike lookback call: payoff = final_price - min_price_over_life
    #min_prices = np.minimum(np.min(price_paths, axis=1), min_price)  # Ensure min price is at most the given min_price
    min_prices = np.min(price_paths, axis = 1)
    final_prices = price_paths[:, -1]
    payoffs = np.maximum(final_prices - min_prices, 0)
    payoffs_after_fee = payoffs * (1 + fee)

    uptonow_payoff = np.maximum(final_prices - min_price, 0)

    value = np.maximum(uptonow_payoff, payoffs_after_fee)

    # Discount payoffs to present value
    option_price = np.exp(-rate * time) * np.mean(value)
    option_price = option_price * (1 + fee)  # Apply fee

    return option_price


if __name__ == "__main__":
    price = 225.74
    volatility = 0.1285
    exppected_return = 0.0
    rate = 0.03
    time = (16 - 1)/252
    min_price = 223.65
    "225.74 12.85 0.08 16 223.65 283.9926393563352"

    print(lookback_option(price, volatility, exppected_return, rate, time, min_price = min_price, nb_paths=1000))

    print(lookback_option(price, volatility, exppected_return, rate, time, min_price = min_price, nb_paths=1000000))

if __name__ == "__main_":
    # Example parameters
    price = 100  # Initial asset price
    volatility = 0.2  # Volatility of the underlying asset (20%)
    expected_return = 0.05  # Expected return of the asset (5%)
    rate = 0.03  # Risk-free interest rate (3%)
    time = 1/12  # Time to maturity in years
    nb_paths = 100  # Number of simulated paths

    option_price = lookback_option(price, volatility, expected_return, rate, time, nb_paths=nb_paths)
    print(f"Estimated Lookback Option Price: {option_price:.2f}")

    tests = 10
    start = t.time()
    for i in range(tests):
        option_price = lookback_option(price, volatility, expected_return, rate, time, nb_paths=100000)
    print(t.time() - start)

    x = []
    y = []
    for i in range(20, 30):
        n = int(10**(i/5))
        x.append(i/5)
        option_price = lookback_option(price, volatility, expected_return, rate, time, nb_paths=n)
        y.append(option_price)
    plt.plot(x,y)
    plt.show()
