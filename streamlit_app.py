import streamlit as st
import numpy as np
import datetime
import matplotlib.pyplot as plt
import scipy.stats as stats

#######################
# Page configuration
st.set_page_config(
    page_title="Monte Carlo Option Pricing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS to inject into Streamlit
st.markdown("""
<style>
/* Adjust the size and alignment of the CALL value container */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px;
    width: auto;
    margin: 0 auto;
}

/* Custom class for the value */
.metric-call {
    background-color: #90ee90;
    color: black;
    border-radius: 10px;
}

/* Style for the value text */
.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
}

/* Style for the label text */
.metric-label {
    font-size: 1rem;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# Monte Carlo Simulation Function
def monte_carlo_option_pricing(S, K, vol, r, N, M, market_value, start_date, end_date):
    # Calculate the time to maturity in years
    T = (end_date - start_date).days / 365.0
    st.write(f"Time to maturity (T) is: {T:.4f} years")

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

    # Compute Expectation and SE
    ST = np.exp(lnSt)
    CT = np.maximum(0, ST[-1] - K)
    C0 = np.exp(-r * T) * np.sum(CT) / M

    sigma = np.sqrt(np.sum((CT - C0)**2) / (M - 1))
    SE = sigma / np.sqrt(M)

    return C0, SE

# Sidebar for User Inputs
with st.sidebar:
    st.title("📊 Monte Carlo Model")
    st.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/mprudhvi/"
    st.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Prudhvi Reddy, Muppala`</a>', unsafe_allow_html=True)

    S = st.number_input("Current Asset Price", value=101.15)
    K = st.number_input("Strike Price", value=98.01)
    vol = st.number_input("Volatility (σ)", value=0.0991)
    r = st.number_input("Risk-Free Interest Rate", value=0.01)
    N = st.number_input("Number of Time Steps (N)", value=10, min_value=1)
    M = st.number_input("Number of Simulations (M)", value=1000, min_value=1)
    market_value = st.number_input("Market Value of Option", value=3.86)

    start_year = st.number_input("Start Year", value=2022)
    start_month = st.number_input("Start Month", value=1, min_value=1, max_value=12)
    start_day = st.number_input("Start Day", value=17, min_value=1, max_value=31)
    end_year = st.number_input("End Year", value=2022)
    end_month = st.number_input("End Month", value=3, min_value=1, max_value=12)
    end_day = st.number_input("End Day", value=17, min_value=1, max_value=31)

    start_date = datetime.date(start_year, start_month, start_day)
    end_date = datetime.date(end_year, end_month, end_day)

# Main Page for Output Display
st.title("Monte Carlo Pricing Model")

# Calculate Call values using Monte Carlo simulation
C0, SE = monte_carlo_option_pricing(S, K, vol, r, N, M, market_value, start_date, end_date)

# Display Call Value with Standard Error in colored table
st.markdown(f"""
    <div class="metric-container metric-call">
        <div>
            <div class="metric-label">CALL Value</div>
            <div class="metric-value">${C0:.2f} ± {SE:.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Display Market Value for comparison
st.write(f"Market Value of the Option: ${market_value:.2f}")

# Plotting the result distribution
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
st.pyplot(plt.gcf())
