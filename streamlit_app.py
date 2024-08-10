import streamlit as st
import numpy as np
import datetime
import plotly.graph_objs as go

#######################
# Page configuration
st.set_page_config(
    page_title="Interactive Monte Carlo Option Pricing with Profitability",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

# Custom CSS to inject into Streamlit
st.markdown("""
<style>
/* Adjust the size and alignment of the CALL and PUT value containers */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 12px;
    width: 100%;
    margin: 10px 0;
}

/* Custom classes for CALL and PUT values */
.metric-call {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    margin-right: 10px;
}

.metric-put {
    background-color: #F44336;
    color: white;
    border-radius: 10px;
}

/* Style for the value text */
.metric-value {
    font-size: 1.7rem;
    font-weight: bold;
    margin: 0;
}

/* Style for the label text */
.metric-label {
    font-size: 1.2rem;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# Monte Carlo Simulation Function for Profitability
def monte_carlo_profitability(S, K, vol, r, N, M, market_value, start_date, end_date):
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

    # Simulated paths for ST
    ST = np.exp(lnSt)

    # Calculate Payoffs at Maturity
    call_payoff = np.maximum(0, ST[-1] - K)
    put_payoff = np.maximum(0, K - ST[-1])

    # Calculate Breakeven Points
    call_breakeven = K + market_value
    put_breakeven = K - market_value

    return ST[-1], call_payoff, put_payoff, call_breakeven, put_breakeven

# Sidebar for User Inputs
st.sidebar.title("📊 Monte Carlo Model")
st.sidebar.write("`Created by:`")
linkedin_url = "www.linkedin.com/in/khaled-sahbi-161329200"
st.sidebar.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Khaled Sahbi`</a>', unsafe_allow_html=True)

# Using expanders to make the interface less compact
with st.sidebar.expander("Option Parameters", expanded=True):
    S = st.number_input("Current Asset Price", value=100.0)
    K = st.number_input("Strike Price", value=105.0)
    vol = st.number_input("Volatility (σ)", value=0.20)
    r = st.number_input("Risk-Free Interest Rate", value=0.03)

with st.sidebar.expander("Simulation Parameters", expanded=False):
    N = st.number_input("Number of Time Steps (N)", value=252, step=1)
    M = st.number_input("Number of Simulations (M)", value=100, step=1)
    market_value = st.number_input("Market Value of Option", value=7.50)

with st.sidebar.expander("Dates", expanded=False):
    start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2025, 1, 1))

# Main Page for Output Display
st.title("Monte Carlo Pricing Model with Profitability Graphing")

# Calculate the paths and payoffs
ST, call_payoff, put_payoff, call_breakeven, put_breakeven = monte_carlo_profitability(S, K, vol, r, N, M, market_value, start_date, end_date)

# Plot the Payoffs
fig = go.Figure()

# Plot Call Payoff
fig.add_trace(go.Scatter(x=ST, y=call_payoff, mode='markers', name='Call Payoff', marker=dict(color='#4CAF50')))
# Plot Put Payoff
fig.add_trace(go.Scatter(x=ST, y=put_payoff, mode='markers', name='Put Payoff', marker=dict(color='#F44336')))

# Add Breakeven Points
fig.add_vline(x=call_breakeven, line=dict(color='#4CAF50', dash='dot'), annotation_text='Call Breakeven', annotation_position='bottom right')
fig.add_vline(x=put_breakeven, line=dict(color='#F44336', dash='dot'), annotation_text='Put Breakeven', annotation_position='bottom left')

# Improving the aesthetics
fig.update_layout(title='Option Payoff vs. Asset Price at Maturity',
                  xaxis_title='Underlying Asset Price at Maturity',
                  yaxis_title='Option Payoff',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, traceorder="normal"),
                  template='plotly_white',
                  margin=dict(l=50, r=50, t=50, b=50))

# Update annotations to avoid overlap
fig.update_annotations(dict(font_size=12, arrowcolor="rgba(0,0,0,0)"))

st.plotly_chart(fig, use_container_width=True)

# Display Market Value for comparison
st.write(f"Market Value of the Option: ${market_value:.2f}")

