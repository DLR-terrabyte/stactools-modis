import xml.etree.ElementTree as ET

import pystac
from pystac import MediaType
from pystac.utils import str_to_datetime
from pystac.extensions.eo import EOExtension, Band
from pystac.extensions.item_assets import ItemAssetsExtension, AssetDefinition
from shapely.geometry import shape

import stactools.modis.fragment
from stactools.modis.constants import (ITEM_TIF_IMAGE_NAME, ITEM_METADATA_NAME)


def create_collection(catalog_id: str) -> pystac.Collection:
    """Creates a STAC Collection for MODIS data.
    """
    fragment = stactools.modis.fragment.load_collection(catalog_id)
    collection = pystac.Collection(
        id=catalog_id,
        description=fragment["description"],
        extent=fragment["extent"],
        title=fragment["title"],
        providers=fragment["providers"],
    )
    collection.add_links(fragment["links"])

    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = {
        "image":
        AssetDefinition({
            "eo:bands":
            stactools.modis.fragment.load_bands(catalog_id),
            "roles": ["data"],
            "title":
            "RGBIR COG tile",
            "type":
            MediaType.COG,
        })
    }

    return collection


def create_item(metadata_href: str) -> pystac.Item:
    """Creates a STAC Item from modis data.
    Args:
        metadata_href (str): The href to the metadata for this hdf.
    This function will read the metadata file for information to place in
    the STAC item.
    Returns:
        pystac.Item: A STAC Item representing this MODIS image.
    """

    metadata_root = ET.parse(metadata_href).getroot()

    # Item id
    name = metadata_root.find('GranuleURMetaData/CollectionMetaData/ShortName')
    assert name is not None
    version = metadata_root.find(
        'GranuleURMetaData/CollectionMetaData/VersionID')
    assert version is not None
    short_item_id = '{}/00{}/{}'.format('MODIS', version.text, name.text)

    image_name = metadata_root.find(
        'GranuleURMetaData/DataFiles/DataFileContainer/DistributedFileName')
    assert image_name is not None
    assert image_name.text is not None
    item_id = image_name.text.replace('.hdf', '')

    coordinates = []
    point_ele = '{}/{}'.format(
        'GranuleURMetaData/SpatialDomainContainer/',
        'HorizontalSpatialDomainContainer/GPolygon/Boundary/Point')
    for point in metadata_root.findall(point_ele):
        lon = point.find('PointLongitude')
        assert lon is not None
        assert lon.text is not None
        lat = point.find('PointLatitude')
        assert lat is not None
        assert lat.text is not None
        coordinates.append([float(lon.text), float(lat.text)])

    geom = {'type': 'Polygon', 'coordinates': [coordinates]}

    bounds = shape(geom).bounds

    # Item date
    prod_node = 'GranuleURMetaData/ECSDataGranule/ProductionDateTime'
    prod_dt_text = metadata_root.find(prod_node)
    assert prod_dt_text is not None
    assert prod_dt_text.text is not None
    prod_dt = str_to_datetime(prod_dt_text.text)

    item = pystac.Item(
        id=item_id,
        geometry=geom,
        bbox=bounds,
        datetime=prod_dt,
        properties=stactools.modis.fragment.load_item_properties(
            short_item_id))

    # Common metadata
    collection = stactools.modis.fragment.load_collection(short_item_id)
    item.common_metadata.providers = collection["providers"]
    item.common_metadata.description = collection["description"]

    instrument_short_name = metadata_root.find(
        'GranuleURMetaData/Platform/Instrument/InstrumentShortName')
    assert instrument_short_name is not None
    assert instrument_short_name.text is not None
    item.common_metadata.instruments = [instrument_short_name.text]
    platform_short_name = metadata_root.find(
        'GranuleURMetaData/Platform/PlatformShortName')
    assert platform_short_name is not None
    item.common_metadata.platform = platform_short_name.text
    item.common_metadata.title = collection["title"]

    # Hdf
    item.add_asset(
        ITEM_TIF_IMAGE_NAME,
        pystac.Asset(href=image_name.text,
                     media_type=pystac.MediaType.HDF,
                     roles=['data'],
                     title="hdf image"))

    # Metadata
    item.add_asset(
        ITEM_METADATA_NAME,
        pystac.Asset(href=image_name.text + '.xml',
                     media_type=pystac.MediaType.TEXT,
                     roles=['metadata'],
                     title='FGDC Metdata'))

    # Bands
    eo = EOExtension.ext(item.assets[ITEM_TIF_IMAGE_NAME], add_if_missing=True)
    eo.bands = [
        Band(band)
        for band in stactools.modis.fragment.load_bands(short_item_id)
    ]

    return item
