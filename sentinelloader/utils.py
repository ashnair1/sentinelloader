import logging
import os
import sys

import requests
from osgeo import gdal, ogr
from pyproj import Transformer
from shapely.geometry import Polygon

logger = logging.getLogger("sentinelloader")


def gmlToPolygon(gmlStr):
    footprint1 = ogr.CreateGeometryFromGML(gmlStr)
    coords = []
    if footprint1.GetGeometryCount() == 1:
        g0 = footprint1.GetGeometryRef(0)
        for i in range(g0.GetPointCount()):
            pt = g0.GetPoint(i)
            coords.append((pt[1], pt[0]))
    return Polygon(coords)


def downloadFile(url, filepath, user, password):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))

    with open(filepath, "wb") as f:
        logger.debug("Downloading %s to %s" % (url, filepath))
        response = requests.get(url, auth=(user, password), stream=True)
        if response.status_code != 200:
            raise Exception("Could not download file. status=%s" % response.status_code)
        total_length = response.headers.get("content-length")

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ("=" * done, " " * (50 - done)))
                sys.stdout.flush()


def saveFile(filename, contents):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, "w") as fw:
        fw.write(contents)
        fw.flush()


def loadFile(filename):
    with open(filename, "r") as fr:
        return fr.read()


def crs_transform(x, y, src_crs=4326, dst_crs=3857):
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    return transformer.transform(x, y)


def convertGeoJSONFromWGS84To3857(geojson):
    c = geojson["coordinates"][0]
    coords = [crs_transform(co[0], co[1]) for co in list(c)]
    return {"coordinates": ((tuple(coords)),), "type": geojson["type"]}


def saveGeoTiff(imageDataFloat, outputFile, geoTransform, projection):
    driver = gdal.GetDriverByName("GTiff")
    image_data = driver.Create(
        outputFile,
        imageDataFloat.shape[1],
        imageDataFloat.shape[0],
        1,
        gdal.GDT_Float32,
    )
    image_data.GetRasterBand(1).WriteArray(imageDataFloat)
    image_data.SetGeoTransform(geoTransform)
    image_data.SetProjection(projection)
    image_data.FlushCache()
    image_data = None
