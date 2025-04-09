import math

def norm_cdf(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type.lower() == "call":
        price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    elif option_type.lower() == "put":
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

def black_scholes_greeks(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type.lower() == "call":
        delta = norm_cdf(d1)
        theta = (-S * norm_pdf(d1) * sigma / (2 * math.sqrt(T))) - r * K * math.exp(-r * T) * norm_cdf(d2)
    elif option_type.lower() == "put":
        delta = norm_cdf(d1) - 1
        theta = (-S * norm_pdf(d1) * sigma / (2 * math.sqrt(T))) + r * K * math.exp(-r * T) * norm_cdf(-d2)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    gamma = norm_pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * norm_pdf(d1) * math.sqrt(T) / 100  # Per 1% change in volatility

    return delta, gamma, theta, vega

import streamlit as st

st.markdown("<h1 style='color:#0072B5; font-family:sans-serif;'>🌀 Gamma Bosphorus Option Pricing Tool</h1>", unsafe_allow_html=True)
st.markdown("Built with 🧠 Streamlit · Powered by math · Designed by Hasan", unsafe_allow_html=True)

S = st.number_input("Underlying Price (S)", value=100.0)
K = st.number_input("Strike Price (K)", value=105.0)
T = st.number_input("Time to Maturity (T, in years)", value=1.0, format="%.2f")
r = st.number_input("Risk-free Interest Rate (r)", value=0.05, format="%.4f")
sigma = st.number_input("Volatility (σ)", value=0.2, format="%.4f")
option_type = st.selectbox("Option Type", ["call", "put"])

if st.button("Calculate"):
    try:
        price = black_scholes(S, K, T, r, sigma, option_type)
        st.success(f"{option_type.capitalize()} Option Price: {price:.2f}")
        delta, gamma, theta, vega = black_scholes_greeks(S, K, T, r, sigma, option_type)
        st.write(f"**Delta:** {delta:.4f}")
        st.write(f"**Gamma:** {gamma:.4f}")
        st.write(f"**Theta:** {theta:.4f}")
        st.write(f"**Vega:** {vega:.4f}")
    except Exception as e:
        st.error(f"Error: {e}")