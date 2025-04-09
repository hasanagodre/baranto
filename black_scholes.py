import math
import argparse
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type.lower() == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type.lower() == "put":
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    return price

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Black-Scholes Option Pricing")
    parser.add_argument("--S", type=float, required=True, help="Spot price")
    parser.add_argument("--K", type=float, required=True, help="Strike price")
    parser.add_argument("--T", type=float, required=True, help="Time to maturity (in years)")
    parser.add_argument("--r", type=float, required=True, help="Risk-free interest rate")
    parser.add_argument("--sigma", type=float, required=True, help="Volatility")
    parser.add_argument("--option_type", type=str, choices=["call", "put"], default="call", help="Option type")

    args = parser.parse_args()

    result = black_scholes(args.S, args.K, args.T, args.r, args.sigma, args.option_type)
    print(f"{args.option_type.capitalize()} Option Price: {result:.2f}")