import logging
import warnings
from typing import List, Optional

import pystac
import pystac.utils
from pystac import Collection, Item, MediaType, Summaries
from pystac.extensions.eo import EOExtension
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.raster import RasterExtension
from pystac.extensions.scientific import ScientificExtension
from stactools.core.io import ReadHrefModifier

from stactools.modis.builder import ModisBuilder
from stactools.modis.constants import (
    CLASSIFICATION_EXTENSION_HREF,
    HDF_ASSET_KEY,
    HDF_ASSET_PROPERTIES,
    METADATA_ASSET_KEY,
    METADATA_ASSET_PROPERTIES,
)
from stactools.modis.product import Product
from stactools.modis.sinusoidal import update_geometry

logger = logging.getLogger(__name__)


def create_collection(product_name: str, version: str) -> Collection:
    """Creates a STAC Collection for MODIS data.

    Args:
        product (str): The ID of a MODIS product, e.g. "MCD12Q1"
        version (str): The MODIS version, e.g. "006" or "061"

    Returns:
        Collection: The created collection.
    """
    product = Product(product_name)
    summaries = {
        "instruments": ["modis"],
        "platform": product.platforms,
    }
    fragments = product.fragments(version)
    item = fragments.item()
    gsd = item.get("gsd")
    if gsd:
        summaries["gsd"] = [gsd]

    fragment = fragments.collection()
    collection = pystac.Collection(
        id=product.collection_id(version),
        description=fragment["description"],
        extent=fragment["extent"],
        title=fragment["title"],
        providers=fragment["providers"],
        keywords=fragment.get("keywords", list()),
        summaries=Summaries(summaries),
    )
    collection.add_links(fragment["links"])

    item_assets_dict = {
        HDF_ASSET_KEY: AssetDefinition(HDF_ASSET_PROPERTIES),
        METADATA_ASSET_KEY: AssetDefinition(METADATA_ASSET_PROPERTIES),
    }
    for name, band in fragments.bands().items():
        if "roles" in band:
            band["roles"].insert(0, "data")
        else:
            band["roles"] = ["data"]
        band["type"] = MediaType.COG
        item_assets_dict[name] = AssetDefinition(band)
        if "eo:bands" in band:
            collection.stac_extensions.append(EOExtension.get_schema_uri())
        if "raster:bands" in band:
            collection.stac_extensions.append(RasterExtension.get_schema_uri())
        if "classification:classes" in band:
            collection.stac_extensions.append(CLASSIFICATION_EXTENSION_HREF)
    collection.stac_extensions = list(set(collection.stac_extensions))
    collection.stac_extensions.sort()
    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = item_assets_dict

    if "sci:publications" in fragment:
        ScientificExtension.add_to(collection)
        # We don't use the scientific extension to set the publications because
        # we don't want duplicate cite-as links.
        collection.extra_fields["sci:publications"] = fragment["sci:publications"]

    return collection


def create_item(
    href: str,
    cog_directory: Optional[str] = None,
    create_cogs: bool = False,
    raster_footprint: bool = False,
    read_href_modifier: Optional[ReadHrefModifier] = None,
    cmr_xml: bool = False,
) -> Item:
    """Creates a STAC Item from MODIS data.

    Args:
        href (str): The href to an HDF file or its metadata.
        cog_directory (str): The directory that will/does hold the COGs. Use
            `create_cogs` to actually create COGs there.
        create_cogs (bool): Should we create cogs from the source data? If so, put
            them in `cog_directory`, or if that is `None`, put them alongside the
            hdf file.
        raster_footprint (bool): Create the Item geometry from the convex
            hull of valid raster data. Has no effect if `create_cogs` is False.
        read_href_modifier (Callable[[str], str]): An optional function to
            modify the href (e.g. to add a token to a url)
        cmr_xml (bool): The CMR metadata format is used (default: False)

    Returns:
        pystac.Item: A STAC Item representing this MODIS image.
    """
    builder = ModisBuilder(
        read_href_modifier=read_href_modifier,
        cmr_xml=cmr_xml,
    )
    builder.add_hdf_or_xml_href(
        href, cog_directory=cog_directory, create_cogs=create_cogs
    )
    item = builder.create_item()
    if raster_footprint:
        if create_cogs:
            update_geometry(item, builder.metadata.collection)
        else:
            raise ValueError(
                "The 'create_cogs' option must be True to use "
                "the 'raster_footprint' option."
            )
    return item


def create_item_from_cogs(
    hrefs: List[str],
    raster_footprint: bool = False,
    read_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Creates a STAC Item from COG paths.

    Args:
        hrefs (str): The hrefs to COGs.
        raster_footprint (bool): Create the Item geometry from the convex
            hull of valid raster data?
        read_href_modifier (Callable[[str], str]): An optional function to
            modify the href (e.g. to add a token to a url)

    Returns:
        pystac.Item: A STAC Item representing this MODIS image.
    """
    builder = ModisBuilder(
        read_href_modifier=read_href_modifier,
    )
    for href in hrefs:
        builder.add_cog_href(href)
    item = builder.create_item()
    if raster_footprint:
        update_geometry(item, builder.metadata.collection)
    return item


def collection_id(product: str, version: str) -> str:
    """Creates a collection id from a product and a version:

    Args:
        product (str): The MODIS product
        version (str): The MODIS version

    Returns:
        str: The collection id, e.g. "modis-MCD12Q1-006"
    """
    warnings.warn(
        "stactools.modis.stac.collection_id is deprecated, and will be removed in v0.4.0",
        DeprecationWarning,
    )
    return f"modis-{product}-{version}"
