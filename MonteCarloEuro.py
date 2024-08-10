import math
import numpy as np
import pandas as pd
import datetime
import scipy.stats as stats
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

def monte_carlo_option_pricing(S, K, vol, r, N, M, market_value, start_date, end_date, option_type):
    # Calculate the time to maturity in years
    T = (end_date - start_date).days / 365.0
    print(f"Time to maturity (T) is: {T} years")

    # Precompute constants
    dt = T / N
    nudt = (r - 0.5 * vol**2) * dt
    volsdt = vol * np.sqrt(dt)
    lnS = np.log(S)

    # Monte Carlo Method
    Z = np.random.normal(size=(N, M))
    delta_lnSt = nudt + volsdt * Z
    lnSt = lnS + np.cumsum(delta_lnSt, axis=0)
    lnSt = np.concatenate((np.full(shape=(1, M), fill_value=lnS), lnSt))

    # Compute Expectation and SE based on option type
    ST = np.exp(lnSt)
    if option_type.lower() == 'call':
        CT = np.maximum(0, ST[-1] - K)
    elif option_type.lower() == 'put':
        CT = np.maximum(0, K - ST[-1])
    else:
        print("Invalid option type. Please choose 'call' or 'put'.")
        return

    C0 = np.exp(-r * T) * np.sum(CT) / M

    sigma = np.sqrt(np.sum((CT - C0)**2) / (M - 1))
    SE = sigma / np.sqrt(M)

    print(f"{option_type.capitalize()} value is ${np.round(C0, 2)} with SE +/- ${np.round(SE, 2)}")

    # Plotting the results
    x1 = np.linspace(C0 - 3 * SE, C0 - 1 * SE, 100)
    x2 = np.linspace(C0 - 1 * SE, C0 + 1 * SE, 100)
    x3 = np.linspace(C0 + 1 * SE, C0 + 3 * SE, 100)

    s1 = stats.norm.pdf(x1, C0, SE)
    s2 = stats.norm.pdf(x2, C0, SE)
    s3 = stats.norm.pdf(x3, C0, SE)

    plt.fill_between(x1, s1, color='tab:blue', label='> StDev')
    plt.fill_between(x2, s2, color='cornflowerblue', label='1 StDev')
    plt.fill_between(x3, s3, color='tab:blue')

    plt.plot([C0, C0], [0, max(s2) * 1.1], 'k', label='Theoretical Value')
    plt.plot([market_value, market_value], [0, max(s2) * 1.1], 'r', label='Market Value')

    plt.ylabel("Probability")
    plt.xlabel("Option Price")
    plt.legend()
    plt.show()

# Prompt the user for input values
option_type = input("Enter the option type ('call' or 'put'): ")
S = float(input("Enter the stock price (S): "))
K = float(input("Enter the strike price (K): "))
vol = float(input("Enter the volatility (% as a decimal): "))
r = float(input("Enter the risk-free rate (% as a decimal): "))
N = int(input("Enter the number of time steps (N): "))
M = int(input("Enter the number of simulations (M): "))
market_value = float(input("Enter the market price of the option: "))

# Prompt the user for start and end dates
start_year = int(input("Enter the start year (YYYY): "))
start_month = int(input("Enter the start month (MM): "))
start_day = int(input("Enter the start day (DD): "))
end_year = int(input("Enter the end year (YYYY): "))
end_month = int(input("Enter the end month (MM): "))
end_day = int(input("Enter the end day (DD): "))

start_date = datetime.date(start_year, start_month, start_day)
end_date = datetime.date(end_year, end_month, end_day)

# Call the function with the user inputs
monte_carlo_option_pricing(S, K, vol, r, N, M, market_value, start_date, end_date, option_type)
