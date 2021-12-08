"""exp2 data"""

import ee
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_images(coordinates_1, dates_1, coordinates_0, dates_0):
    """
    [summary]

    Parameters
    ----------
    coordinates_1 : [type]
        [description]
    dates_1 : [type]
        [description]
    coordinates_0 : [type]
        [description]
    dates_0 : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    
    # Creating empty lists

    geo_list_1 = []
    b_sar_list_1 = []
    a_sar_list_1 = []
    b_landsat_list_1 = []
    a_landsat_list_1 = []

    geo_list_0 = []
    b_sar_list_0 = []
    a_sar_list_0 = []
    b_landsat_list_0 = []
    a_landsat_list_0 = []

    # Converting coordinates into ee geometry points
    for i in range(0, len(coordinates_1)):
        c_1 = ee.Geometry.Point(coordinates_1[i])
        g_1 = c_1.buffer(1000)
        geo_list_1.append(g_1)

        md_1 = ee.Date(dates_1[i])
        sd_1 = md_1.advance(-4, "week")
        ed_1 = md_1.advance(4, "week")

        b_sar_1 = (
            ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
            .filterBounds(c_1)
            .filterDate(sd_1, md_1)
            .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
            .limit(1, "system:time_start", False)
            .first()
        )
        a_sar_1 = (
            ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
            .filterBounds(c_1)
            .filterDate(md_1, ed_1)
            .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
            .first()
        )
        b_sar_list_1.append(b_sar_1)
        a_sar_list_1.append(a_sar_1)

        b_landsat_1 = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
            .filterBounds(c_1)
            .filterDate(sd_1, md_1)
            .sort("CLOUD_COVER")
            .limit(1, "system:time_start", False)
            .first()
        )
        a_landsat_1 = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
            .filterBounds(c_1)
            .filterDate(md_1, ed_1)
            .sort("CLOUD_COVER")
            .first()
        )
        b_landsat_list_1.append(b_landsat_1)
        a_landsat_list_1.append(a_landsat_1)

        c_0 = ee.Geometry.Point(coordinates_0[i])
        g_0 = c_0.buffer(1000)
        geo_list_0.append(g_0)

        md_0 = ee.Date(dates_0[i])
        sd_0 = md_0.advance(-4, "week")
        ed_0 = md_0.advance(4, "week")

        b_sar_0 = (
            ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
            .filterBounds(c_0)
            .filterDate(sd_0, md_0)
            .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
            .limit(1, "system:time_start", False)
            .first()
        )
        a_sar_0 = (
            ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
            .filterBounds(c_0)
            .filterDate(md_0, ed_0)
            .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
            .first()
        )
        b_sar_list_0.append(b_sar_0)
        a_sar_list_0.append(a_sar_0)

        b_landsat_0 = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
            .filterBounds(c_0)
            .filterDate(sd_0, md_0)
            .sort("CLOUD_COVER")
            .limit(1, "system:time_start", False)
            .first()
        )
        a_landsat_0 = (
            ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
            .filterBounds(c_0)
            .filterDate(md_0, ed_0)
            .sort("CLOUD_COVER")
            .first()
        )
        b_landsat_list_0.append(b_landsat_0)
        a_landsat_list_0.append(a_landsat_0)

    return (
        b_sar_list_1,
        a_sar_list_1,
        b_landsat_list_1,
        a_landsat_list_1,
        geo_list_1,
        b_sar_list_0,
        a_sar_list_0,
        b_landsat_list_0,
        a_landsat_list_0,
        geo_list_0,
    )
