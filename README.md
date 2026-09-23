# Hong Kong Earthquake Catastrophe Model

A simplified catastrophe model estimating earthquake loss for 
55,206 buildings in the Kowloon Peninsula, Hong Kong.

## Objective
Estimate the annual aggregate earthquake loss distribution and 
produce an exceedance probability (EP) curve for reinsurance pricing.

## Data Sources
- Building footprints: Lands Department (CSDI Portal)
- Study area: Lands Department Historical Maps (HK1980 Grid)

## Methodology

### 1. Exposure
- 55,206 active buildings in Kowloon
- Insured value = footprint area × floors × HK$20,000/m²
- Total insured value: HK$5.36 trillion

### 2. Hazard
- Fault zone: offshore, SE of Hong Kong
- Magnitude: Gutenberg-Richter, M 4.0–6.0, b = 0.75
- GMPE: ln(PGA) = -1.5 + 0.75M - 1.2 ln(R+20), capped at 1.0g
- Site amplification: 1.2×
- Event frequency: λ = 0.1 events/year

### 3. Vulnerability
- Lognormal fragility curve
- Median PGA = 0.55g, β = 0.50

### 4. Simulation
- 10,000-year Monte Carlo
- ~1,100 simulated events

## Key Results

| Metric | Value |
|---|---|
| Total insured value | HK$ 5.36 trillion |
| Mean annual loss | HK$ 14.7 million |
| 1-in-100 year loss | HK$ 19.1 million |
| 1-in-250 year loss | HK$ 244.8 million |
| 1-in-500 year loss | HK$ 955.4 million |

![EP Curve](ep_curve.png)

## How to Run

The scripts are designed to run in order:

1. `catm_verify.py` — Visual overlay of historical map and modern 
   buildings (verification only)
2. `catm_exposure.py` — Build the exposure table from building 
   footprints
3. `catm_hazard.py` — Simulate one earthquake event to verify the 
   hazard layer
4. `catm_vulnerability.py` — Convert PGA to damage ratio for the 
   example event
5. `catm_simulation.py` — Run the full 10,000-year Monte Carlo 
   simulation
6. `catm_EP.py` — Generate the exceedance probability curve

**Install dependencies first:**

    pip install -r requirements.txt

**Note:** The input data files (building footprints, historical map) 
are not included in this repo due to size. Download from:
- Buildings: CSDI Portal
- Historical map: DATA.GOV.HK

## Limitations
- Construction type and building age not modeled
- Single vulnerability curve for all buildings
- Simplified GMPE without site-specific soil data
- Fault zone is a geometric simplification

## Tools
Python (GeoPandas, NumPy, Pandas, Matplotlib, Rasterio, SciPy)
