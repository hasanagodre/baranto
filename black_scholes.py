import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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

    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # Sabit parametreler
    K = 105  # Strike price
    r = 0.05  # Risk-free rate

    # Grid parametreleri
    S_values = np.linspace(80, 130, 50)  # Underlying prices
    T_values = np.linspace(0.01, 1.0, 50)  # Time to maturity (in years)
    sigma_values = np.linspace(0.1, 0.5, 50)  # Volatility

    # 3D grid üret
    S_grid, T_grid, sigma_grid = np.meshgrid(S_values, T_values, sigma_values, indexing="ij")

    # Fiyat hesaplama fonksiyonu vektörize
    def vectorized_bs(S, K, T, r, sigma):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    prices = vectorized_bs(S_grid, K, T_grid, r, sigma_grid)

    # 3B grafik çizimi
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Ortadan bir sigma dilimi seç (örnek: 0.3)
    sigma_idx = np.abs(sigma_values - 0.3).argmin()
    Z = prices[:, :, sigma_idx]

    X, Y = np.meshgrid(S_values, T_values, indexing="ij")
    ax.plot_surface(X, Y, Z, cmap='viridis')

    ax.set_title("Call Option Price vs Underlying Price & Time to Maturity (σ=0.3)")
    ax.set_xlabel("Underlying Price (S)")
    ax.set_ylabel("Time to Maturity (T)")
    ax.set_zlabel("Option Price")

    plt.tight_layout()
    plt.show()