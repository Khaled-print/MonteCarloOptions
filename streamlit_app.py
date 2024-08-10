import streamlit as st
import numpy as np
import datetime
import plotly.graph_objs as go
import scipy.stats as stats

#######################
# Page configuration
st.set_page_config(
    page_title="Interactive Monte Carlo Option Pricing with Greeks",
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

# Monte Carlo Simulation Function with Greeks Calculation
def monte_carlo_option_pricing_with_greeks(S, K, vol, r, N, M, market_value, start_date, end_date):
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
    
    # Compute Expectation and SE for Call Option
    CT = np.maximum(0, ST[-1] - K)
    C0 = np.exp(-r * T) * np.sum(CT) / M

    # Compute Expectation and SE for Put Option
    PT = np.maximum(0, K - ST[-1])
    P0 = np.exp(-r * T) * np.sum(PT) / M

    # Calculate Standard Errors
    sigma_call = np.sqrt(np.sum((CT - C0)**2) / (M - 1))
    SE_call = sigma_call / np.sqrt(M)

    sigma_put = np.sqrt(np.sum((PT - P0)**2) / (M - 1))
    SE_put = sigma_put / np.sqrt(M)

    # Calculate ITM and OTM counts
    itm_calls = np.sum(ST[-1] > K)
    otm_calls = np.sum(ST[-1] <= K)
    itm_puts = np.sum(ST[-1] < K)
    otm_puts = np.sum(ST[-1] >= K)

    # Calculate ITM and OTM as percentages
    itm_calls_pct = itm_calls / M * 100
    otm_calls_pct = otm_calls / M * 100
    itm_puts_pct = itm_puts / M * 100
    otm_puts_pct = otm_puts / M * 100

    # Calculate profitability
    profitable_calls = np.sum((ST[-1] - K) > C0)
    profitable_puts = np.sum((K - ST[-1]) > P0)
    profitable_calls_pct = profitable_calls / M * 100
    profitable_puts_pct = profitable_puts / M * 100

    # Greeks Calculation
    delta_call = np.mean(ST[-1] > K)  # ∆ Call (approximated by the proportion of paths that end up ITM)
    delta_put = np.mean(ST[-1] < K)   # ∆ Put (approximated by the proportion of paths that end up ITM)
    
    # Gamma can be approximated as the change in Delta for a small change in S
    epsilon = S * 0.01
    ST_up = ST * np.exp(volsdt)
    ST_down = ST * np.exp(-volsdt)
    
    delta_call_up = np.mean(ST_up[-1] > K)
    delta_call_down = np.mean(ST_down[-1] > K)
    
    gamma_call = (delta_call_up - delta_call_down) / (2 * epsilon)
    gamma_put = gamma_call  # Gamma is the same for calls and puts

    # Vega is approximated by rerunning the simulation with slightly higher volatility
    volsdt_up = (vol + epsilon) * np.sqrt(dt)
    lnSt_up = lnS + np.cumsum(nudt + volsdt_up * Z, axis=0)
    ST_up_vol = np.exp(lnSt_up)

    CT_up_vol = np.maximum(0, ST_up_vol[-1] - K)
    C0_up_vol = np.exp(-r * T) * np.sum(CT_up_vol) / M
    vega_call = (C0_up_vol - C0) / epsilon

    PT_up_vol = np.maximum(0, K - ST_up_vol[-1])
    P0_up_vol = np.exp(-r * T) * np.sum(PT_up_vol) / M
    vega_put = (P0_up_vol - P0) / epsilon

    # Theta is approximated by rerunning the simulation with a slightly shorter maturity
    T_down = T - dt
    lnSt_down = lnS + np.cumsum(nudt * (T_down/T) + volsdt * np.sqrt(T_down/T) * Z, axis=0)
    ST_down = np.exp(lnSt_down)

    CT_down = np.maximum(0, ST_down[-1] - K)
    C0_down = np.exp(-r * T_down) * np.sum(CT_down) / M
    theta_call = (C0_down - C0) / dt

    PT_down = np.maximum(0, K - ST_down[-1])
    P0_down = np.exp(-r * T_down) * np.sum(PT_down) / M
    theta_put = (P0_down - P0) / dt

    # Rho is approximated by rerunning the simulation with a slightly higher interest rate
    r_up = r + epsilon
    nudt_up = (r_up - 0.5 * vol**2) * dt
    lnSt_up = lnS + np.cumsum(nudt_up + volsdt * Z, axis=0)
    ST_up = np.exp(lnSt_up)

    CT_up = np.maximum(0, ST_up[-1] - K)
    C0_up = np.exp(-r_up * T) * np.sum(CT_up) / M
    rho_call = (C0_up - C0) / epsilon

    PT_up = np.maximum(0, K - ST_up[-1])
    P0_up = np.exp(-r_up * T) * np.sum(PT_up) / M
    rho_put = (P0_up - P0) / epsilon

    return C0, SE_call, P0, SE_put, itm_calls_pct, otm_calls_pct, itm_puts_pct, otm_puts_pct, delta_call, delta_put, gamma_call, gamma_put, vega_call, vega_put, theta_call, theta_put, rho_call, rho_put, profitable_calls_pct, profitable_puts_pct

# Sidebar for User Inputs
st.sidebar.title("📊 Monte Carlo Model")
st.sidebar.write("`Created by:`")
linkedin_url = "www.linkedin.com/in/khaled-sahbi-161329200"
st.sidebar.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Khaled Sahbi`</a>', unsafe_allow_html=True)

# Using expanders to make the interface less compact
with st.sidebar.expander("Option Parameters", expanded=True):
    S = st.number_input("Current Asset Price", value=100.0)
    K = st.number_input("Strike Price", value=100.0)
    vol = st.number_input("Volatility (σ)", value=0.2)
    r = st.number_input("Risk-Free Interest Rate", value=0.03)

with st.sidebar.expander("Simulation Parameters", expanded=False):
    N = st.number_input("Number of Time Steps (N)", value=252, step=1)
    M = st.number_input("Number of Simulations (M)", value=500, step=100)
    market_value = st.number_input("Market Value of Option", value=10.0)

with st.sidebar.expander("Dates", expanded=False):
    start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2025, 1, 1))

# Main Page for Output Display
st.title("Monte Carlo Pricing Model with Greeks")

# Calculate Call and Put values using Monte Carlo simulation
results = monte_carlo_option_pricing_with_greeks(S, K, vol, r, N, M, market_value, start_date, end_date)
(C0, SE_call, P0, SE_put, itm_calls_pct, otm_calls_pct, itm_puts_pct, otm_puts_pct, 
 delta_call, delta_put, gamma_call, gamma_put, vega_call, vega_put, theta_call, theta_put, rho_call, rho_put, profitable_calls_pct, profitable_puts_pct) = results

# Display Call and Put Values with Standard Errors in colored tables
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div class="metric-container metric-call">
            <div>
                <div class="metric-label">CALL Value</div>
                <div class="metric-value">${C0:.2f} ± {SE_call:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-container metric-put">
            <div>
                <div class="metric-label">PUT Value</div>
                <div class="metric-value">${P0:.2f} ± {SE_put:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ITM and OTM details in an expander
with st.expander("In the Money (ITM) and Out of the Money (OTM) Percentages", expanded=False):
    st.write(f"**Call Options:** ITM: {itm_calls_pct:.2f}%, OTM: {otm_calls_pct:.2f}%")
    st.write(f"**Put Options:** ITM: {itm_puts_pct:.2f}%, OTM: {otm_puts_pct:.2f}%")

# Profitability details in an expander
with st.expander("Profitability Percentages", expanded=False):
    st.write(f"**Profitable Call Options:** {profitable_calls_pct:.2f}%")
    st.write(f"**Profitable Put Options:** {profitable_puts_pct:.2f}%")

# Display Market Value for comparison
st.write(f"Market Value of the Option: ${market_value:.2f}")

# Display Greeks
st.subheader("Option Greeks")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Delta (Call):** {delta_call:.4f}")
    st.write(f"**Gamma (Call):** {gamma_call:.4f}")
    st.write(f"**Vega (Call):** {vega_call:.4f}")
    st.write(f"**Theta (Call):** {theta_call:.4f}")
    st.write(f"**Rho (Call):** {rho_call:.4f}")
with col2:
    st.write(f"**Delta (Put):** {delta_put:.4f}")
    st.write(f"**Gamma (Put):** {gamma_put:.4f}")
    st.write(f"**Vega (Put):** {vega_put:.4f}")
    st.write(f"**Theta (Put):** {theta_put:.4f}")
    st.write(f"**Rho (Put):** {rho_put:.4f}")

# Interactive Plot with Plotly
x_call = np.linspace(C0 - 3 * SE_call, C0 + 3 * SE_call, 100)
y_call = stats.norm.pdf(x_call, C0, SE_call)

x_put = np.linspace(P0 - 3 * SE_put, P0 + 3 * SE_put, 100)
y_put = stats.norm.pdf(x_put, P0, SE_put)

fig = go.Figure()

# Call Option Plot
fig.add_trace(go.Scatter(x=x_call, y=y_call, mode='lines', name='Call Option', line=dict(color='#4CAF50', width=2)))

# Put Option Plot
fig.add_trace(go.Scatter(x=x_put, y=y_put, mode='lines', name='Put Option', line=dict(color='#F44336', width=2)))

# Vertical Lines
fig.add_vline(x=C0, line=dict(color='#4CAF50', dash='dash'), annotation_text='Call Value', annotation_position='top right')
fig.add_vline(x=P0, line=dict(color='#F44336', dash='dash'), annotation_text='Put Value', annotation_position='top left')
fig.add_vline(x=market_value, line=dict(color='#2196F3'), annotation_text='Market Value', annotation_position='top right')

# Improving the aesthetics
fig.update_layout(title='Option Pricing Distribution',xaxis_title='Option Price',
                  yaxis_title='Probability Density',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, traceorder="normal"),
                  template='plotly_white',
                  margin=dict(l=50, r=50, t=50, b=50))

# Update annotations to avoid overlap
fig.update_annotations(dict(font_size=12, arrowcolor="rgba(0,0,0,0)"))

st.plotly_chart(fig, use_container_width=True)
