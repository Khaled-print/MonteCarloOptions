import streamlit as st
import numpy as np
import datetime
import plotly.graph_objs as go
import scipy.stats as stats

#######################
# Page configuration
st.set_page_config(
    page_title="Interactive Monte Carlo Option Pricing",
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

    # Compute Expectation and SE for Call Option
    ST = np.exp(lnSt)
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

    return C0, SE_call, P0, SE_put

# Sidebar for User Inputs
st.sidebar.title("📊 Monte Carlo Model")
st.sidebar.write("`Created by:`")
linkedin_url = "www.linkedin.com/in/khaled-sahbi-161329200"
st.sidebar.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Khaled Sahbi`</a>', unsafe_allow_html=True)

# Using expanders to make the interface less compact
with st.sidebar.expander("Option Parameters", expanded=True):
    S = st.slider("Current Asset Price", min_value=90.0, max_value=110.0, value=100.0, step=0.1)
    K = st.slider("Strike Price", min_value=90.0, max_value=110.0, value=100.0, step=0.1)
    vol = st.slider("Volatility (σ)", min_value=0.01, max_value=0.5, value=0.2, step=0.01)
    r = st.slider("Risk-Free Interest Rate", min_value=0.0, max_value=0.1, value=0.03, step=0.01)

with st.sidebar.expander("Simulation Parameters", expanded=False):
    N = st.slider("Number of Time Steps (N)", min_value=1, max_value=365, value=252, step=1)
    M = st.slider("Number of Simulations (M)", min_value=100, max_value=1000, value=500, step=100)
    market_value = st.number_input("Market Value of Option", value=10.0)

with st.sidebar.expander("Dates", expanded=False):
    start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
    end_date = st.date_input("End Date", datetime.date(2025, 1, 1))

# Main Page for Output Display
st.title("Monte Carlo Pricing Model")

# Calculate Call and Put values using Monte Carlo simulation
C0, SE_call, P0, SE_put = monte_carlo_option_pricing(S, K, vol, r, N, M, market_value, start_date, end_date)

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

# Display Market Value for comparison
st.write(f"Market Value of the Option: ${market_value:.2f}")

# Interactive Plot with Plotly
x_call = np.linspace(C0 - 3 * SE_call, C0 + 3 * SE_call, 100)
y_call = stats.norm.pdf(x_call, C0, SE_call)

x_put = np.linspace(P0 - 3 * SE_put, P0 + 3 * SE_put, 100)
y_put = stats.norm.pdf(x_put, P0, SE_put)

fig = go.Figure()

# Call Option Plot
fig.add_trace(go.Scatter(x=x_call, y=y_call, mode='lines', name='Call Option', line=dict(color='#4CAF50', width=2)))
fig.add_trace(go.Scatter(x=x_call, y=y_call, fill='tozeroy', fillcolor='rgba(76, 175, 80, 0.3)', mode='none'))

# Put Option Plot
fig.add_trace(go.Scatter(x=x_put, y=y_put, mode='lines', name='Put Option', line=dict(color='#F44336', width=2)))
fig.add_trace(go.Scatter(x=x_put, y=y_put, fill='tozeroy', fillcolor='rgba(244, 67, 54, 0.3)', mode='none'))

# Vertical Lines
fig.add_vline(x=C0, line=dict(color='#4CAF50', dash='dash'), annotation_text='Call Value', annotation_position='top right')
fig.add_vline(x=P0, line=dict(color='#F44336', dash='dash'), annotation_text='Put Value', annotation_position='top left')
fig.add_vline(x=market_value, line=dict(color='#2196F3'), annotation_text='Market Value', annotation_position='top right')

# Improving the aesthetics
fig.update_layout(title='Option Pricing Distribution',
                  xaxis_title='Option Price',
                  yaxis_title='Probability Density',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, traceorder="normal"),
                  template='plotly_white',
                  margin=dict(l=50, r=50, t=50, b=50))

# Update annotations to avoid overlap
fig.update_annotations(dict(font_size=12, arrowcolor="rgba(0,0,0,0)"))

st.plotly_chart(fig, use_container_width=True)

