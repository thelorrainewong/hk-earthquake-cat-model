'''
Purpose:
    Visual overlay of the historical Kowloon 1970 map with modern 
    building footprints, to verify CRS alignment and to identify 
    old vs. new building clusters for the exposure layer.

Inputs:
    - Building_Outline_Public_v20260819_Building_converted.geojson
      (Lands Department building footprints, CSDI Portal)
    - HIST-HE08-1970.tif
      (Historical map of Kowloon from Lands Department)

Outputs:
    - overlay_check.png  (map + building footprints on top), showing the map and building footprints are aligned.

Notes:
    - This script is for visual verification only.
'''

import matplotlib
matplotlib.use("Agg")  

import rasterio
from rasterio.plot import show
import geopandas as gpd
import matplotlib.pyplot as plt

buildings = gpd.read_file(
    "Building_Outline_Public_v20260819_Building_converted.geojson"
).to_crs(epsg=2326)

with rasterio.open("HIST-HE08-1970.tif") as src:
    left, bottom, right, top = src.bounds
    study_buildings = buildings.cx[left:right, bottom:top]
    print(f"Buildings in study area: {len(study_buildings)}")

    factor = 8
    arr = src.read(1, out_shape=(src.height // factor, src.width // factor))
    transform = src.transform * src.transform.scale(factor)

    fig, ax = plt.subplots(figsize=(16, 16))
    show(arr, transform=transform, ax=ax, cmap="gray", alpha=0.75)
    study_buildings.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=0.4)
    ax.set_title("Kowloon 1970 + Modern Buildings")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    plt.tight_layout()
    plt.savefig("overlay_check.png", dpi=150)
    plt.close(fig)

print("Saved overlay_check.png")
