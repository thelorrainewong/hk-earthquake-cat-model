'''
Purpose:
    Define fault zone and simulate one earthquake event, for 
    verification only. This script checks that the hazard layer 
    produces realistic PGA values before running the full simulation.

Inputs:
    - exposure_kowloon.csv  (from catm_exposure.py)

Outputs:
    - Console output only (example event statistics)

Notes:
    - This is a verification script, not the full simulation.
'''

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Load exposure
exposure = pd.read_csv(SCRIPT_DIR / "exposure_kowloon.csv")
print(f"Loaded {len(exposure)} buildings")

bx = exposure["easting"].values
by = exposure["northing"].values

FAULT_ZONE = {
    "x_min": 880000, "x_max": 960000,
    "y_min": 760000, "y_max": 820000,
}

M_MIN = 4.0
M_MAX = 6.0
B_VALUE = 0.75

rng = np.random.default_rng(42)


def sample_epicenter(n):
    x = rng.uniform(FAULT_ZONE["x_min"], FAULT_ZONE["x_max"], n)
    y = rng.uniform(FAULT_ZONE["y_min"], FAULT_ZONE["y_max"], n)
    return x, y


def sample_magnitude(n):
    u = rng.uniform(0, 1, n)
    m = M_MIN - (1.0 / B_VALUE) * np.log10(u)
    return np.clip(m, M_MIN, M_MAX)


def compute_pga(magnitude, distance_km):
    ln_pga = -1.5 + 0.75 * magnitude - 1.2 * np.log(distance_km + 20)
    pga = np.exp(ln_pga)
    return np.minimum(pga, 1.0)


def simulate_event():
    ex_arr, ey_arr = sample_epicenter(1)
    ex = float(ex_arr[0])
    ey = float(ey_arr[0])
    M = float(sample_magnitude(1)[0])
    dx = bx - ex
    dy = by - ey
    dist_km = np.sqrt(dx**2 + dy**2) / 1000.0
    pga = compute_pga(M, dist_km)
    return M, ex, ey, dist_km, pga


# Simulate one event, for verification only
M, ex, ey, dist_km, pga = simulate_event()

idx_nearest = np.argmin(dist_km)
idx_farthest = np.argmax(dist_km)

print(f"\nExample event:")
print(f"  Epicenter: ({ex:.0f}, {ey:.0f})")
print(f"  Magnitude: {M:.2f}")
print(f"  Distance range: {dist_km.min():.1f}-{dist_km.max():.1f} km")
print(f"  PGA range: {pga.min():.4f}-{pga.max():.4f} g")
print(f"  PGA at nearest ({dist_km[idx_nearest]:.1f} km): {pga[idx_nearest]:.4f} g")
print(f"  PGA at farthest ({dist_km[idx_farthest]:.1f} km): {pga[idx_farthest]:.4f} g")

print(f"\nCorrelation (should be NEGATIVE): {np.corrcoef(dist_km, pga)[0, 1]:.3f}")