"""Generate figures for sampling_distributions_lecture1.qmd"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.stats import chi2, t as t_dist

# ── Figure 1: Return Histograms ──────────────────────────────────────────────

symbols = ["^GSPC", "^GDAXI", "^N225"]
names   = {"^GSPC": "S&P 500", "^GDAXI": "DAX (Germany)", "^N225": "Nikkei 225"}
colors  = {"^GSPC": "#2196F3",  "^GDAXI": "#4CAF50",        "^N225": "#FF5722"}

all_returns = {}
for sym in symbols:
    data = yf.download(sym, start="2020-01-01", end="2025-01-01", progress=False)
    returns = data["Close"].squeeze().pct_change().dropna() * 100   # in %
    all_returns[sym] = returns

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
fig.suptitle("Daily Returns: S&P 500, DAX, Nikkei 225  (Jan 2020 – Jan 2025)",
             fontsize=13, fontweight="bold", y=1.02)

for ax, sym in zip(axes, symbols):
    ret = all_returns[sym]
    mu, sigma = ret.mean(), ret.std()
    ax.hist(ret, bins=60, density=True, alpha=0.55,
            color=colors[sym], edgecolor="white", linewidth=0.3)
    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 300)
    ax.plot(x, stats.norm.pdf(x, mu, sigma), color="black", lw=1.8,
            label=f"N({mu:.3f}, {sigma:.3f}²)")
    ax.set_title(names[sym], fontsize=11, fontweight="bold")
    ax.set_xlabel("Daily Return (%)", fontsize=9)
    ax.set_ylabel("Density", fontsize=9)
    ax.legend(fontsize=8)
    ax.text(0.97, 0.97,
            f"n = {len(ret)}\nμ = {mu:.4f}%\nσ = {sigma:.4f}%",
            transform=ax.transAxes, va="top", ha="right", fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

plt.tight_layout()
plt.savefig("l1_return_histograms.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved l1_return_histograms.png")

# ── Figure 2: Chi-square and t plots ────────────────────────────────────────

# Reproduce the random sample from S&P 500 returns (seed=42, n=25)
sp500 = all_returns["^GSPC"].values
np.random.seed(42)
sample = np.random.choice(sp500, size=25)
n      = len(sample)
ybar   = sample.mean()
s      = sample.std(ddof=1)
t_stat = ybar / (s / np.sqrt(n))
t_crit = t_dist.ppf(0.975, df=n-1)
chi2_95 = chi2.ppf(0.95, df=n-1)

print(f"Sample mean: {ybar:.4f}%  |  std: {s:.4f}%  |  t-stat: {t_stat:.4f}")
print(f"chi2_0.05({n-1}) = {chi2_95:.3f}  |  t_0.025({n-1}) = {t_crit:.4f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

# Left: χ²(24) with shaded tail
df_chi = n - 1
x_chi  = np.linspace(0, 60, 500)
y_chi  = chi2.pdf(x_chi, df=df_chi)
ax1.plot(x_chi, y_chi, color="#1565C0", lw=2.0)
x_shade = np.linspace(chi2_95, 60, 300)
ax1.fill_between(x_shade, chi2.pdf(x_shade, df_chi), alpha=0.35,
                 color="#EF5350", label=f"5% tail")
ax1.axvline(chi2_95, color="#C62828", lw=1.8, linestyle="--",
            label=f"χ²₀.₀₅(24) = {chi2_95:.3f}")
ax1.set_title(f"χ²({df_chi}) Distribution  —  Sample Variance Test", fontsize=11)
ax1.set_xlabel("χ²", fontsize=10)
ax1.set_ylabel("Density", fontsize=10)
ax1.legend(fontsize=9)
ax1.set_xlim(0, 55)

# Right: t(24) with CI region and t-statistic
x_t   = np.linspace(-5, 5, 500)
y_t   = t_dist.pdf(x_t, df=df_chi)
ax2.plot(x_t, y_t, color="#1565C0", lw=2.0, label=f"t({df_chi})")
# shade 95% CI (between -t_crit and t_crit)
x_ci = np.linspace(-t_crit, t_crit, 300)
ax2.fill_between(x_ci, t_dist.pdf(x_ci, df_chi), alpha=0.20,
                 color="#42A5F5", label="95% CI region")
# shade rejection regions
for xlo, xhi in [(-5, -t_crit), (t_crit, 5)]:
    xs = np.linspace(xlo, xhi, 200)
    ax2.fill_between(xs, t_dist.pdf(xs, df_chi), alpha=0.35, color="#EF5350")
ax2.axvline(t_crit, color="#C62828", lw=1.5, linestyle="--",
            label=f"±t₀.₀₂₅(24) = ±{t_crit:.3f}")
ax2.axvline(-t_crit, color="#C62828", lw=1.5, linestyle="--")
ax2.axvline(t_stat, color="#2E7D32", lw=2.2, linestyle="-",
            label=f"t-stat = {t_stat:.3f}")
ax2.set_title(f"t({df_chi}) Distribution  —  H₀: μ = 0 (n = {n})", fontsize=11)
ax2.set_xlabel("t", fontsize=10)
ax2.set_ylabel("Density", fontsize=10)
ax2.legend(fontsize=9)
ax2.set_xlim(-5, 5)

plt.tight_layout()
plt.savefig("l1_chi2_t_plots.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved l1_chi2_t_plots.png")
