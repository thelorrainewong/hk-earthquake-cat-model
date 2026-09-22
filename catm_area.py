'''
Purpose:
    Build the exposure table from Lands Department building footprints.
    Filters to the study area, drops buildings with missing height, 
    and computes insured value for each building.

Inputs:
    - Building_Outline_Public_v20260819_Building_converted.geojson
      (Lands Department building footprints, CSDI Portal)
    - HIST-HE08-1970.tif
      (Historical map of Kowloon, used to define study area bounds)

Outputs:
    - exposure_kowloon.geojson  (exposure table with geometry)
    - exposure_kowloon.csv      (exposure table without geometry)

Notes:
    - Around 12% of buildings are dropped due to missing height values.
    - Insured value assumes HK$20,000 per m² of gross floor area.
    - Input files are not included in this repo due to size. Download 
      from CSDI Portal (buildings) and DATA.GOV.HK (historical map).
'''

import geopandas as gpd
import rasterio
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# Load the building footprints
buildings = gpd.read_file(
    SCRIPT_DIR / "Building_Outline_Public_v20260819_Building_converted.geojson"
).to_crs(epsg=2326)

# Filter to study area (map bounds)
with rasterio.open(SCRIPT_DIR / "HIST-HE08-1970.tif") as src:
    left, bottom, right, top = src.bounds

buildings = buildings.cx[left:right, bottom:top].copy()
buildings = buildings[buildings["Status"] == "Active"].copy()

# Drop buildings with missing height (~12%)
before = len(buildings)
buildings = buildings.dropna(subset=["TopHeight", "BaseHeight"]).copy()
print(f"Dropped {before - len(buildings)} buildings with missing height")

buildings["footprint_area_m2"] = buildings["Shape_Area"]
buildings["height_m"] = (buildings["TopHeight"] - buildings["BaseHeight"]).clip(lower=3)
buildings["floors_est"] = (buildings["height_m"] / 3.0).round().clip(lower=1)
buildings["gross_floor_area_m2"] = (
    buildings["footprint_area_m2"] * buildings["floors_est"]
)

REPLACEMENT_COST_HKD_PER_M2 = 20000
buildings["insured_value"] = (
    buildings["gross_floor_area_m2"] * REPLACEMENT_COST_HKD_PER_M2
)

exposure = buildings[[
    "BuildingID", "BuildingBlockType", "Status", "geometry",
    "footprint_area_m2", "height_m", "floors_est",
    "gross_floor_area_m2", "insured_value",
]].copy()

exposure["easting"] = exposure.geometry.centroid.x
exposure["northing"] = exposure.geometry.centroid.y

print(f"Exposure count: {len(exposure)}")
print(exposure[["footprint_area_m2", "height_m",
                "gross_floor_area_m2", "insured_value"]].describe().round(1))

exposure.to_file(SCRIPT_DIR / "exposure_kowloon.geojson", driver="GeoJSON")
exposure.drop(columns="geometry").to_csv(
    SCRIPT_DIR / "exposure_kowloon.csv", index=False
)
print("Saved exposure_kowloon.geojson / .csv")