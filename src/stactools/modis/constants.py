from typing import Any, Dict

from pystac import MediaType

CLASSIFICATION_EXTENSION_HREF = (
    "https://stac-extensions.github.io/classification/v1.0.0/schema.json"
)
HDF_ASSET_KEY = "hdf"
HDF_ASSET_PROPERTIES = {
    "type": MediaType.HDF,
    "roles": ["data"],
    "title": "Source data containing all bands",
}
METADATA_ASSET_KEY = "metadata"
METADATA_ASSET_PROPERTIES = {
    "type": MediaType.XML,
    "roles": ["metadata"],
    "title": "Federal Geographic Data Committee (FGDC) Metadata",
}
TEMPORALLY_WEIGHTED_PRODUCTS = ["MCD43A4"]

PRECISION = 6

# Sinusoidal projection parameters derived from Appendix 2, Section 13.1 in:
# https://modis-fire.umd.edu/files/MODIS_Burned_Area_Collection51_User_Guide_3.1.0.pdf
# All parameters specified to 12 significant digits. This assures we retain
# millimeter precision at the projection extremeties.
SINUSOIDAL_SPHERE_RADIUS = 6371007.18100
SINUSOIDAL_TILE_METERS = 1111950.51977
SINUSOIDAL_X_MIN = -20015109.3558
SINUSOIDAL_Y_MAX = 10007554.6779
# fmt: off
COLLECTION_FOOTPRINT_METADATA: Dict[str, Dict[str, Any]] = {
    "11A1": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["LST_Day_1km", "LST_Night_1km", "Emis_31", "Emis_32"],
    },
    "11A2": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["LST_Day_1km", "LST_Night_1km", "Emis_31", "Emis_32"],
    },
    "14A1": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["FireMask"],
        "footprint_asset_bands": [],
    },
    "14A2": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["FireMask"],
        "footprint_asset_bands": [],
    },
    "21A2": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["LST_Day_1km", "LST_Night_1km", "Emis_31", "Emis_32"],
    },
    "09A1": {
        "sin_tile_pixels": 2400,
        "footprint_assets": [f"sur_refl_b0{b}" for b in range(1, 8)],
    },
    "09GA": {
        "sin_tile_pixels": 2400,
        "footprint_assets": [f"sur_refl_b0{b}" for b in range(1, 8)],
    },
    "09GQ": {
        "sin_tile_pixels": 4800,
        "footprint_assets": [f"sur_refl_b0{b}" for b in range(1, 3)],
    },
    "10A1": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["NDSI_Snow_Cover", "Snow_Albedo_Daily_Tile"],
    },
    "10A2": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Maximum_Snow_Extent"]
    },
    "12Q1": {
        "sin_tile_pixels": 2400
    },
    "13A1": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["500m_16_days_NDVI"]
    },
    "13A2": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["1km_16_days_NDVI"]
    },
    "13A3": {
        "sin_tile_pixels": 1200,
        "footprint_assets": ["1km_monthly_NDVI"]
    },
    "13Q1": {
        "sin_tile_pixels": 4800,
        "footprint_assets": ["250m_16_days_NDVI"]
    },
    "15A2H": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Fpar_500m"]
    },
    "15A3H": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Fpar_500m"]
    },
    "16A3GF": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["ET_500m"]
    },
    "17A2H": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Gpp_500m"]
    },
    "17A2HGF": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Gpp_500m"]
    },
    "17A3HGF": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Gpp_500m"]
    },
    "43A4": {
        "sin_tile_pixels": 2400,
        "footprint_assets": [f"Nadir_Reflectance_Band{b}" for b in range(1, 8)],
    },
    "44W": {
        "sin_tile_pixels": 2400
    },
    "64A1": {
        "sin_tile_pixels": 2400,
        "footprint_assets": ["Burn_Date"]
    },
    "09Q1": {
        "sin_tile_pixels": 4800,
        "footprint_assets": ["sur_refl_b01", "sur_refl_b02"],
    },
    "13Q1": {
        "sin_tile_pixels": 4800,
        "footprint_assets": ["250m_16_days_NDVI"]
    },
    "44B": {
        "sin_tile_pixels": 4800
    }
}
# fmt:on
