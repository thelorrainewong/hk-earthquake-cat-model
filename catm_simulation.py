'''
Purpose:
    Run the full 10,000-year Monte Carlo simulation of earthquake 
    events and compute annual aggregate losses for the Kowloon 
    building portfolio.

Inputs:
    - exposure_kowloon.csv  (from catm_exposure.py)

Outputs:
    - annual_losses.npy  (10,000 annual loss values)
    - annual_losses.csv  (same data in CSV format)

Notes:
    - Hazard: GMPE with near-field saturation, capped at 1.0g.
    - Magnitude: Gutenberg-Richter, M 4.0-6.0, b = 0.75.
    - Frequency: Poisson, lambda = 0.1 events/year.
    - Vulnerability: lognormal fragility, median PGA 0.55g, beta 0.50.
    - Site amplification: 1.2x.
    - Uses numpy only (no scipy dependency).
'''

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
from pathlib import Path
from math import erf

SCRIPT_DIR = Path(__file__).parent

# Load exposure
exposure = pd.read_csv(SCRIPT_DIR / "exposure_kowloon.csv")
print(f"Loaded {len(exposure)} buildings")

bx = exposure["easting"].values
by = exposure["northing"].values
insured_value = exposure["insured_value"].values

# Parameters, calibrated to give realistic outputs
LAMBDA = 0.1
M_MIN = 4.0
M_MAX = 6.0
B_VALUE = 0.75
N_YEARS = 10000
SITE_AMPLIFICATION = 1.2

FAULT_ZONE = {
    "x_min": 880000, "x_max": 960000,
    "y_min": 760000, "y_max": 820000,
}

# Vulnerability parameters
VULN_MEDIAN_PGA = 0.55
VULN_BETA = 0.50


def lognorm_cdf(x, s, scale):
    x = np.asarray(x)
    z = (np.log(np.maximum(x, 1e-12)) - np.log(scale)) / (s * np.sqrt(2))
    return 0.5 * (1 + np.vectorize(erf)(z))


def damage_ratio(pga):
    return lognorm_cdf(pga, VULN_BETA, VULN_MEDIAN_PGA)


def compute_pga(magnitude, distance_km):
    ln_pga = -1.5 + 0.75 * magnitude - 1.2 * np.log(distance_km + 20)
    pga = np.exp(ln_pga)
    return np.minimum(pga, 1.0)


rng = np.random.default_rng(42)


def sample_magnitude():
    u = rng.uniform()
    m = M_MIN - (1.0 / B_VALUE) * np.log10(u)
    return min(max(m, M_MIN), M_MAX)


# Full simulation (not verification)
annual_losses = np.zeros(N_YEARS)
event_count = 0

for year in range(N_YEARS):
    n_events = rng.poisson(LAMBDA)
    year_loss = 0.0

    for _ in range(n_events):
        ex = rng.uniform(FAULT_ZONE["x_min"], FAULT_ZONE["x_max"])
        ey = rng.uniform(FAULT_ZONE["y_min"], FAULT_ZONE["y_max"])
        M = sample_magnitude()

        dx = bx - ex
        dy = by - ey
        dist_km = np.sqrt(dx**2 + dy**2) / 1000.0

        pga = compute_pga(M, dist_km) * SITE_AMPLIFICATION
        dr = damage_ratio(pga)
        loss = (insured_value * dr).sum()
        year_loss += loss
        event_count += 1

    annual_losses[year] = year_loss

    if (year + 1) % 1000 == 0:
        print(f"  Year {year+1}/{N_YEARS} done, total events: {event_count}")

# Save outputs
np.save("annual_losses.npy", annual_losses)
pd.DataFrame({
    "year": np.arange(N_YEARS),
    "annual_loss": annual_losses,
}).to_csv("annual_losses.csv", index=False)

# Summary
total_insured = exposure["insured_value"].sum()
print(f"\nTotal insured value: HK$ {total_insured:,.0f}")
print(f"Total events simulated: {event_count}")
print(f"Years with zero loss: {(annual_losses == 0).sum()} / {N_YEARS}")
print(f"Mean annual loss: HK$ {annual_losses.mean():,.0f}")
print(f"Max annual loss:  HK$ {annual_losses.max():,.0f}")
print(f"Max / Total insured: {annual_losses.max() / total_insured:.2%}")

non_zero = annual_losses[annual_losses > 0]
if len(non_zero) > 0:
    print(f"\nNon-zero years: {len(non_zero)}")
    print(f"Mean loss (non-zero years): HK$ {non_zero.mean():,.0f}")
    print(f"Median (non-zero): HK$ {np.median(non_zero):,.0f}")

print("\nSaved annual_losses.npy / .csv")