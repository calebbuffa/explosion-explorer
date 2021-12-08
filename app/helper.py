"""app helper"""

import ee
import numpy as np
from exp2.utils.process_image import *


def calculate_difference(coordinate, date, Map, clf) -> None:
    """
    [summary]

    Parameters
    ----------
    coordinate : [type]
        [description]
    date : [type]
        [description]
    Map : [type]
        [description]
    """

    point = ee.Geometry.Point(
        coordinate.getInfo()["features"][0]["geometry"]["coordinates"]
    )
    geometry = point.buffer(1000)  # buffers point by 1 km

    md = ee.Date(date)
    sd = md.advance(-4, "week")
    ed = md.advance(4, "week")

    before_sar = (
        ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
        .filterBounds(point)
        .filterDate(sd, md)
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .limit(1, "system:time_start", False)
        .first()
    )
    after_sar = (
        ee.ImageCollection("COPERNICUS/S1_GRD_FLOAT")
        .filterBounds(point)
        .filterDate(md, ed)
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .first()
    )

    before_landsat = (
        ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
        .filterBounds(point)
        .filterDate(sd, md)
        .sort("CLOUD_COVER")
        .limit(1, "system:time_start", False)
        .first()
    )
    after_landsat = (
        ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
        .filterBounds(point)
        .filterDate(md, ed)
        .sort("CLOUD_COVER")
        .first()
    )

    (
        ndvi_p25,
        ndvi_p50,
        ndvi_p75,
        ndvi_mean,
        ndvi_stddev,
        ndvi_min,
        ndvi_max,
        before_ndvi,
        after_ndvi,
    ) = ndvi(before_landsat, after_landsat, geometry)

    (
        evi_p25,
        evi_p50,
        evi_p75,
        evi_mean,
        evi_stddev,
        evi_min,
        evi_max,
        before_evi,
        after_evi,
    ) = evi(before_landsat, after_landsat, geometry)

    (
        sar_p25,
        sar_p50,
        sar_p75,
        sar_mean,
        sar_stddev,
        sar_min,
        sar_max,
        c_map,
    ) = sar(before_sar, after_sar, geometry)

    (
        nbr_p25_,
        nbr_p50,
        nbr_p75,
        nbr_mean,
        nbr_stddev,
        nbr_min,
        nbr_max,
        before_nbr,
        after_nbr,
    ) = nbr(before_landsat, after_landsat, geometry)

    ar = np.array(
        [
            ndvi_p25,
            ndvi_p50,
            ndvi_p75,
            ndvi_mean,
            ndvi_min,
            ndvi_max,
            evi_p25,
            evi_p50,
            evi_p75,
            evi_mean,
            evi_stddev,
            evi_min,
            evi_max,
            sar_mean,
            sar_stddev,
            sar_max,
            nbr_mean,
            nbr_stddev,
            nbr_p25_,
            nbr_p50,
            nbr_p75,
            nbr_min,
        ]
    ).reshape(1, -1)

    try:
        pred = clf.predict(ar)
        prob = clf.predict_proba(ar)
        if pred[0] == 1:
            pred = f"Explosion Likely Occured On: {date}"
            prob = f"Probability of Explosion: {round(prob[0][1]*100, 2)}%"
        else:
            pred = f"Explosion Did Not Likely Occur On: {date}"
            prob = f"Probability of No Explosion: {round(prob[0][0]*100, 2)}%"
        print(f"{pred}\n{prob}")
    except:
        print("Error: Please choose different location/date")

    try:
        Map.addLayer(
            before_ndvi.clip(geometry),
            {
                "min": 0,
                "max": 1,
                "palette": [
                    "FFFFFF",
                    "CE7E45",
                    "DF923D",
                    "F1B555",
                    "FCD163",
                    "99B718",
                    "74A901",
                    "66A000",
                    "529400",
                    "3E8601",
                    "207401",
                    "056201",
                    "004C00",
                    "023B01",
                    "012E01",
                    "011D01",
                    "011301",
                ],
            },
            "Before NDVI",
        )
    except:
        pass

    try:
        Map.addLayer(
            after_ndvi.clip(geometry),
            {
                "min": 0,
                "max": 1,
                "palette": [
                    "FFFFFF",
                    "CE7E45",
                    "DF923D",
                    "F1B555",
                    "FCD163",
                    "99B718",
                    "74A901",
                    "66A000",
                    "529400",
                    "3E8601",
                    "207401",
                    "056201",
                    "004C00",
                    "023B01",
                    "012E01",
                    "011D01",
                    "011301",
                ],
            },
            "After NDVI",
        )
    except:
        pass

    try:
        Map.addLayer(
            before_evi.clip(geometry),
            {
                "min": 0,
                "max": 1,
                "palette": [
                    "FFFFFF",
                    "CE7E45",
                    "DF923D",
                    "F1B555",
                    "FCD163",
                    "99B718",
                    "74A901",
                    "66A000",
                    "529400",
                    "3E8601",
                    "207401",
                    "056201",
                    "004C00",
                    "023B01",
                    "012E01",
                    "011D01",
                    "011301",
                ],
            },
            "Before EVI",
        )
    except:
        pass

    try:
        Map.addLayer(
            after_evi.clip(geometry),
            {
                "min": 0,
                "max": 1,
                "palette": [
                    "FFFFFF",
                    "CE7E45",
                    "DF923D",
                    "F1B555",
                    "FCD163",
                    "99B718",
                    "74A901",
                    "66A000",
                    "529400",
                    "3E8601",
                    "207401",
                    "056201",
                    "004C00",
                    "023B01",
                    "012E01",
                    "011D01",
                    "011301",
                ],
            },
            "After EVI",
        )
    except:
        pass

    try:
        Map.addLayer(
            before_nbr.clip(geometry),
            {"min": 0, "max": 1, "palette": ["000000", "FFFFFF"]},
            "Before NBR",
        )
    except:
        pass

    try:
        Map.addLayer(
            after_nbr.clip(geometry),
            {"min": 0, "max": 1, "palette": ["000000", "FFFFFF"]},
            "After NBR",
        )
    except:
        pass

    try:
        Map.addLayer(
            c_map.clip(geometry),
            {"palette": ["white", "blue", "red"]},
            "SAR Probability",
        )
    except:
        pass
