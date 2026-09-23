'''
Purpose:
    Read the 10,000 annual losses from the simulation, compute key 
    risk metrics (mean, return-period losses, TVaR), and plot the 
    exceedance probability (EP) curve.

Inputs:
    - annual_losses.npy  (from catm_simulation.py)

Outputs:
    - ep_curve.png   (exceedance probability curve)
    - ep_curve.csv   (loss, exceedance probability, return period)

Notes:
    - Return-period loss = k-th largest loss, where k = N / return_period.
    - This is NOT the same as np.percentile when most years have zero loss.
    - TVaR (Tail Value at Risk) = mean of all losses above the 1-in-100 level.
    - X-axis is in HK$ million for readability.
'''

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Load annual losses
annual_losses = np.load("annual_losses.npy")
print(f"Loaded {len(annual_losses)} years of simulated losses")

# Sort descending, compute exceedance probability
sorted_losses = np.sort(annual_losses)[::-1]
n = len(sorted_losses)
exceedance_prob = np.arange(1, n + 1) / n
return_period = 1.0 / exceedance_prob


def loss_at_return_period(rp):
    k = int(round(n / rp))
    k = max(1, min(k, n))
    return sorted_losses[k - 1]


def format_hkd(value):
    if value >= 1e9:
        return f"HK${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"HK${value/1e6:.1f}M"
    elif value >= 1e3:
        return f"HK${value/1e3:.1f}K"
    else:
        return f"HK${value:.0f}"


# Key risk metrics
mean_loss = annual_losses.mean()
loss_100yr = loss_at_return_period(100)
loss_200yr = loss_at_return_period(200)
loss_250yr = loss_at_return_period(250)
loss_500yr = loss_at_return_period(500)

var_99 = loss_100yr
tvar_99 = annual_losses[annual_losses >= var_99].mean()

print(f"\nKey risk metrics:")
print(f"  Mean annual loss:        {format_hkd(mean_loss)}")
print(f"  1-in-100 year loss:      {format_hkd(loss_100yr)}")
print(f"  1-in-200 year loss:      {format_hkd(loss_200yr)}")
print(f"  1-in-250 year loss:      {format_hkd(loss_250yr)}")
print(f"  1-in-500 year loss:      {format_hkd(loss_500yr)}")
print(f"  TVaR (beyond 1-in-100):  {format_hkd(tvar_99)}")

# Plot EP curve
fig, ax = plt.subplots(figsize=(12, 8))

sorted_losses_m = sorted_losses / 1e6
mask = sorted_losses_m > 0
ax.loglog(sorted_losses_m[mask], exceedance_prob[mask],
          color="navy", linewidth=2, label="EP curve")

for rp, label in [(100, "1-in-100"), (200, "1-in-200"), (500, "1-in-500")]:
    loss_at_rp = loss_at_return_period(rp)
    if loss_at_rp > 0:
        ax.axvline(loss_at_rp / 1e6, color="gray",
                   linestyle="--", alpha=0.6)
        ax.text(loss_at_rp / 1e6, 1e-3,
                f"  {label}\n  {format_hkd(loss_at_rp)}",
                fontsize=9, va="bottom")

ax.set_xlabel("Annual aggregate loss (HK$ million)", fontsize=12)
ax.set_ylabel("Exceedance probability", fontsize=12)
ax.set_title("Exceedance Probability Curve — Hong Kong Earthquake Portfolio",
             fontsize=13)
ax.grid(True, which="both", alpha=0.3)
ax.legend()

fig.text(0.99, 0.01,
         "Source: author's model, 10,000-year Monte Carlo simulation",
         ha="right", fontsize=8, color="gray")

plt.tight_layout()
plt.savefig("ep_curve.png", dpi=150)
plt.close()

# Save EP curve data
ep_df = pd.DataFrame({
    "annual_loss": sorted_losses,
    "exceedance_prob": exceedance_prob,
    "return_period": return_period,
})
ep_df.to_csv("ep_curve.csv", index=False)

print("\nSaved ep_curve.png / ep_curve.csv")