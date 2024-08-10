# Monte Carlo Option Pricing Model with Greeks

## Overview

This repository contains a Python-based implementation of a **Monte Carlo Simulation** model for option pricing. The model focuses on pricing European Call and Put options using a Monte Carlo method, which simulates the price paths of the underlying asset through a Geometric Brownian Motion (GBM). Additionally, the model calculates the option Greeks (Delta, Gamma, Vega, Theta, and Rho), providing a comprehensive view of how various factors affect option prices.

As part of my own venture into self-teaching Python for the quantitative finance industry, I decided to build this simple options pricer as an intro into Stochastic processes which I wish to delve into post-grad undertaking a masters in quantitative finance, until then here is my take on an options pricer. 

### What You’ll Find Here

- **Monte Carlo Simulation**: A robust method for pricing derivatives, particularly when dealing with complex payoffs or when analytical solutions are impractical.
- **Geometric Brownian Motion**: The underlying asset price is modeled using GBM, a standard approach in financial modeling.
- **European Options**: The model is designed to price European-style options, meaning the option can only be exercised at maturity.
- **Option Greeks**: The model calculates Delta, Gamma, Vega, Theta, and Rho, which are essential for understanding the sensitivity of option prices to various factors.

## How It Works

### Geometric Brownian Motion (GBM)

The price of the underlying asset \( S(t) \) evolves over time according to the following stochastic process:

S(t + Δt) = S(t) * exp[(r - 0.5 * σ^2) * Δt + σ * sqrt(Δt) * Z]
- **S(t)**: The asset price at time \( t \).
- **r**: The risk-free interest rate.
- **σ**: The volatility of the asset.
- **Z**: A random variable drawn from a standard normal distribution (mean = 0, variance = 1).

### Simulating Price Paths

The Monte Carlo simulation generates multiple paths for the asset price, each representing a potential scenario for how the asset might behave over time until maturity. For each path, the payoff of the option is calculated.

### Option Payoff Calculation

At maturity, the payoffs are determined as follows:

- **Call Option**: `max(S(T) - K, 0)`
- **Put Option**: `max(K - S(T), 0)`

Where:

- **S(T)**: The simulated asset price at maturity.
- **K**: The strike price of the option.

### Pricing the Option

The option price is derived from the expected value of the payoff, discounted at the risk-free rate:

Option Price = exp(-r * T) * (1/M) * Σ(Payoff_i)

Where:

- **M**: The number of simulated paths.

### Tracking In the Money (ITM) and Out of the Money (OTM) Outcomes

To provide additional insights, the model tracks how often the options are In the Money (ITM) or Out of the Money (OTM) at maturity:

- **Call Option ITM**: When `S(T) > K`
- **Put Option ITM**: When `S(T) < K`

These metrics help in evaluating the likelihood of profitable outcomes and can be used for P&L tracking.

### Option Greeks

The model also calculates the following Greeks:

- **Delta (Δ)**: Sensitivity of the option price to changes in the underlying asset's price.
- **Gamma (Γ)**: Rate of change of Delta with respect to changes in the underlying asset's price.
- **Vega (ν)**: Sensitivity of the option price to changes in volatility.
- **Theta (Θ)**: Sensitivity of the option price to the passage of time.
- **Rho (ρ)**: Sensitivity of the option price to changes in the risk-free interest rate.

These Greeks are crucial for managing risk and understanding how various factors affect the option’s price.

## How to Use

### Inputs

- **Current Asset Price (S)**: The spot price of the underlying asset.
- **Strike Price (K)**: The exercise price of the option.
- **Volatility (σ)**: The standard deviation of the asset’s returns, representing uncertainty.
- **Risk-Free Interest Rate (r)**: The theoretical rate of return on a risk-free investment.
- **Number of Time Steps (N)**: Discretization of the time to maturity.
- **Number of Simulations (M)**: The number of price paths to simulate.

### Outputs

- **Call and Put Option Prices**: The estimated value of the options.
- **Standard Errors**: The statistical error in the estimated option prices.
- **ITM/OTM Percentages**: Frequency of the option being In the Money or Out of the Money at maturity.
- **Option Greeks**: Delta, Gamma, Vega, Theta, and Rho.

### Visualization

The model includes a visualization feature that plots the probability distribution of the option prices, along with indicators for the calculated call and put prices, as well as the market value.

## Conclusion

This Monte Carlo Option Pricing Model is a tool for evaluating European options in scenarios where traditional models like Black-Scholes might fall short. Its flexibility, the ability to track ITM and OTM outcomes, and the inclusion of option Greeks provide a comprehensive view of potential market conditions. This is my first project ever, and I have a strong interest in quantitative finance, particularly algorithmic trading.

### Inspiration

The calculation methodology for the Monte Carlo was inspired by QuantPy’s YouTube video on **Monte Carlo Simulation for Stock Portfolio**. I thought it would be cool to create an interactive options version that lets you play with variables interactively and also included greeks, and ITM/OTM reports to give a more complete tool for option pricing.

I have tweaked the initial calculation methodology to enable calculations for both 'call' and 'put' options. The code, unlike the original, will prompt the user for input variables, run said variables through GBM & Payoff calculations, and produce values and a plotted Monte Carlo distribution. Additionally, the inclusion of option Greeks makes the tool more robust and informative for practical use, particularly in risk management and trading strategies. 

