"""preprocess"""

import ee
import numpy as np
import pandas as pd

ee.Initialize()

reducers = (
    ee.Reducer.mean()
    .combine(**{"reducer2": ee.Reducer.stdDev(), "sharedInputs": True})
    .combine(**{"reducer2": ee.Reducer.max(), "sharedInputs": True})
    .combine(**{"reducer2": ee.Reducer.min(), "sharedInputs": True})
    .combine(
        **{
            "reducer2": ee.Reducer.percentile([25, 50, 75]),
            "sharedInputs": True,
        }
    )
)


def det(im):
    """
    [summary]

    Parameters
    ----------
    im : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    return im.expression("b(0) * b(1)")


def chi2cdf(chi2, df):
    """
    Chi square cumulative distribution function for df degrees of freedom
    using the built-in incomplete gamma function gammainc()

    Parameters
    ----------
    chi2 : [type]
        [description]
    df : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    return ee.Image(chi2.divide(2)).gammainc(ee.Number(df).divide(2))


def sar(before, after, geometry):
    """
    [summary]

    Parameters
    ----------
    before : [type]
        [description]
    after : [type]
        [description]
    geometry : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    m = 5

    try:
        # The observed test statistic image -2logq
        m2logq = (
            det(before)
            .log()
            .add(det(after).log())
            .subtract(det(before.add(after)).log().multiply(2))
            .add(4 * np.log(2))
            .multiply(-2 * m)
        )

        # The P value image prob(m2logQ > m2logq) = 1 - prob(m2logQ < m2logq).
        p_value = ee.Image.constant(1).subtract(chi2cdf(m2logq, 2))

        c_map = p_value.multiply(0).where(p_value.lt(0.05), 1)

        diff = after.subtract(
            before
        )  # Getting the difference between the two images
        d_map = c_map.multiply(0)  # Initialize the direction map to zero.
        d_map = d_map.where(
            det(diff).gt(0), 1
        )  # All pos or neg def diffs are now labeled 1.
        d_map = d_map.where(
            diff.select(0).gt(0), 2
        )  # Re-label pos def (and label some indef) to 2.
        d_map = d_map.where(det(diff).lt(0), 1)  # Label all indef to 1.
        c_map = c_map.multiply(
            d_map
        )  # Re-label the c_map, 0*X = 0, 1*1 = 1, 1*2= 2, 1*3 = 3.

        stats = c_map.reduceRegion(
            **{
                "reducer": reducers,
                "bestEffort": True,
                "scale": 30,
                "geometry": geometry,
            }
        ).getInfo()
        mean = stats["constant_mean"]
        stddev = stats["constant_stdDev"]
        p25 = stats["constant_p25"]
        p50 = stats["constant_p50"]
        p75 = stats["constant_p75"]
        min = stats["constant_min"]
        max = stats["constant_max"]
    except:
        mean = None
        stddev = None
        p25 = None
        p50 = None
        p75 = None
        min = None
        max = None

    return p25, p50, p75, mean, stddev, min, max


def sar_difference(before, after, geometry):
    """
    [summary]

    Parameters
    ----------
    before : [type]
        [description]
    after : [type]
        [description]
    geometry : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    mean_list = []
    stddev_list = []
    p25_list = []
    p50_list = []
    p75_list = []
    min_list = []
    max_list = []

    for i in range(0, len(before), 1000):

        mean, stddev, p25, p50, p75, min, max = sar(
            before[i], after[i], geometry[i]
        )

        mean_list.append(mean)
        stddev_list.append(stddev)
        p25_list.append(p25)
        p50_list.append(p50)
        p75_list.append(p75)
        min_list.append(min)
        max_list.append(max)

        print(f"Image {i} Done")

    return pd.DataFrame(
        list(
            zip(
                mean_list,
                stddev_list,
                p25_list,
                p50_list,
                p75_list,
                min_list,
                max_list,
            )
        ),
        columns=[
            "SAR_mean",
            "SAR_stdDev",
            "SAR_p25",
            "SAR_p50",
            "SAR_p75",
            "SAR_min",
            "SAR_max",
        ],
    )


def ndvi(before, after, geometry):
    """
    [summary]

    Parameters
    ----------
    before : [type]
        [description]
    after : [type]
        [description]
    geometry : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    try:
        stats_b = (
            before.normalizedDifference(["B5", "B4"])
            .rename("NDVI")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )
        stats_a = (
            after.normalizedDifference(["B5", "B4"])
            .rename("NDVI")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )

        mean_b = stats_b["NDVI_mean"]
        mean_a = stats_a["NDVI_mean"]

        p25_b = stats_b["NDVI_p25"]
        p25_a = stats_a["NDVI_p25"]

        p50_b = stats_b["NDVI_p50"]
        p50_a = stats_a["NDVI_p50"]

        p75_b = stats_b["NDVI_p75"]
        p75_a = stats_a["NDVI_p75"]

        stddev_b = stats_b["NDVI_stdDev"]
        stddev_a = stats_a["NDVI_stdDev"]

        min_b = stats_b["NDVI_min"]
        min_a = stats_a["NDVI_min"]

        max_b = stats_b["NDVI_max"]
        max_a = stats_a["NDVI_max"]

        p25 = p25_a - p25_b * 100
        p50 = p50_a - p50_b * 100
        p75 = p75_a - p50_b * 100
        mean = mean_a - mean_b * 100
        min = min_a - min_b * 100
        max = max_a - max_b * 100
        stddev = stddev_a - stddev_b * 100

    except:
        p25 = None
        p50 = None
        p75 = None
        mean = None
        stddev = None
        min = None
        max = None

    return p25, p50, p75, mean, stddev, min, max


def ndvi_difference(before, after, geometry):
    p25_list = []
    p50_list = []
    p75_list = []
    mean_list = []
    stddev_list = []
    min_list = []
    max_list = []

    for i in range(0, len(before), 100):
        p25, p50, p75, mean, stddev, min, max = ndvi(
            before[i], after[i], geometry[i]
        )
        p25_list.append(p25)
        p50_list.append(p50)
        p75_list.append(p75)
        mean_list.append(mean)
        stddev_list.append(stddev)
        min_list.append(min)
        max_list.append(max)

        print(f"mage {i} Done")

    return pd.DataFrame(
        list(
            zip(
                p25_list,
                p50_list,
                p75_list,
                mean_list,
                stddev_list,
                min_list,
                max_list,
            )
        ),
        columns=[
            "NDVI_p25",
            "NDVI_p50",
            "NDVI_p75",
            "NDVI_mean",
            "NDVI_stdDev",
            "NDVI_min",
            "NDVI_max",
        ],
    )


def nbr(before, after, geometry):
    """
    [summary]

    Parameters
    ----------
    before : [type]
        [description]
    after : [type]
        [description]
    geometry : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    try:
        stats_b = (
            before.normalizedDifference(["B5", "B7"])
            .rename("NBR")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )
        stats_a = (
            after.normalizedDifference(["B5", "B7"])
            .rename("NBR")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )

        mean_b = stats_b["NBR_mean"]
        mean_a = stats_a["NBR_mean"]

        p25_b = stats_b["NBR_p25"]
        p25_a = stats_a["NBR_p25"]

        p50_b = stats_b["NBR_p50"]
        p50_a = stats_a["NBR_p50"]

        p75_b = stats_b["NBR_p75"]
        p75_a = stats_a["NBR_p75"]

        stddev_b = stats_b["NBR_stdDev"]
        stddev_a = stats_a["NBR_stdDev"]

        min_b = stats_b["NBR_min"]
        min_a = stats_a["NBR_min"]

        max_b = stats_b["NBR_max"]
        max_a = stats_a["NBR_max"]

        p25 = p25_a - p25_b * 100
        p50 = p50_a - p50_b * 100
        p75 = p75_a - p50_b * 100
        mean = mean_a - mean_b * 100
        min = min_a - min_b * 100
        max = max_a - max_b * 100
        stddev = stddev_a - stddev_b * 100

    except:
        p25 = None
        p50 = None
        p75 = None
        mean = None
        stddev = None
        min = None
        max = None

    return p25, p50, p75, mean, stddev, min, max


def nbr_difference(before, after, geometry):
    p25_list = []
    p50_list = []
    p75_list = []
    mean_list = []
    stddev_list = []
    min_list = []
    max_list = []

    for i in range(len(before)):
        p25, p50, p75, mean, stddev, min, max = nbr(
            before[i], after[i], geometry[i]
        )
        p25_list.append(p25)
        p50_list.append(p50)
        p75_list.append(p75)
        mean_list.append(mean)
        stddev_list.append(stddev)
        min_list.append(min)
        max_list.append(max)

        print(f"Image {i} Done")

    return pd.DataFrame(
        list(
            zip(
                p25_list,
                p50_list,
                p75_list,
                mean_list,
                stddev_list,
                min_list,
                max_list,
            )
        ),
        columns=[
            "NBR_p25",
            "NBR_p50",
            "NBR_p75",
            "NBR_mean",
            "NBR_stdDev",
            "NBR_min",
            "NBR_max",
        ],
    )


def evi(before, after, geometry):
    """
    [summary]

    Parameters
    ----------
    before : [type]
        [description]
    after : [type]
        [description]
    geometry : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    try:
        before_evi = before.expression(
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
            {
                "NIR": before.select("B5"),
                "RED": before.select("B4"),
                "BLUE": before.select("B2"),
            },
        )

        after_evi = after.expression(
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
            {
                "NIR": after.select("B5"),
                "RED": after.select("B4"),
                "BLUE": after.select("B2"),
            },
        )

        stats_b = (
            before_evi.rename("EVI")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )
        stats_a = (
            after_evi.rename("EVI")
            .reduceRegion(
                **{
                    "reducer": reducers,
                    "bestEffort": True,
                    "scale": 30,
                    "geometry": geometry,
                }
            )
            .getInfo()
        )

        mean_b = stats_b["EVI_mean"]
        mean_a = stats_a["EVI_mean"]

        p25_b = stats_b["EVI_p25"]
        p25_a = stats_a["EVI_p25"]

        p50_b = stats_b["EVI_p50"]
        p50_a = stats_a["EVI_p50"]

        p75_b = stats_b["EVI_p75"]
        p75_a = stats_a["EVI_p75"]

        stddev_b = stats_b["EVI_stdDev"]
        stddev_a = stats_a["EVI_stdDev"]

        min_b = stats_b["EVI_min"]
        min_a = stats_a["EVI_min"]

        max_b = stats_b["EVI_max"]
        max_a = stats_a["EVI_max"]

        p25 = p25_a - p25_b * 100
        p50 = p50_a - p50_b * 100
        p75 = p75_a - p50_b * 100
        mean = mean_a - mean_b * 100
        min = min_a - min_b * 100
        max = max_a - max_b * 100
        stddev = stddev_a - stddev_b * 100

    except:
        p25 = None
        p50 = None
        p75 = None
        mean = None
        stddev = None
        min = None
        max = None

    return p25, p50, p75, mean, stddev, min, max


def evi_difference(before, after, geometry):
    p25_list = []
    p50_list = []
    p75_list = []
    mean_list = []
    stddev_list = []
    min_list = []
    max_list = []

    for i in range(len(before)):
        p25, p50, p75, mean, stddev, min, max = evi(
            before[i], after[i], geometry[i]
        )
        p25_list.append(p25)
        p50_list.append(p50)
        p75_list.append(p75)
        mean_list.append(mean)
        stddev_list.append(stddev)
        min_list.append(min)
        max_list.append(max)

        print(f"mage {i} Done")

    return pd.DataFrame(
        list(
            zip(
                p25_list,
                p50_list,
                p75_list,
                mean_list,
                stddev_list,
                min_list,
                max_list,
            )
        ),
        columns=[
            "EVI_p25",
            "EVI_p50",
            "EVI_p75",
            "EVI_mean",
            "EVI_stdDev",
            "EVI_min",
            "EVI_max",
        ],
    )
