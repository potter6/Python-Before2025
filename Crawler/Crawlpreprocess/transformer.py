import numpy as np
import re

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323


def gcj02towgs84(lng, lat):
    """
    Convert coordinates from GCJ02 to WGS84

    Parameters
    -------
    lng : Series or number
        Longitude
    lat : Series or number
        Latitude

    return
    -------
    lng : Series or number
        Longitude (Converted)
    lat : Series or number
        Latitude (Converted)
    """
    try:
        lng = lng.astype(float)
        lat = lat.astype(float)
    except Exception:
        lng = float(lng)
        lat = float(lat)
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = np.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = np.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * np.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return lng * 2 - mglng, lat * 2 - mglat


def transformlat(lng, lat):
    ret = (
        -100.0
        + 2.0 * lng
        + 3.0 * lat
        + 0.2 * lat * lat
        + 0.1 * lng * lat
        + 0.2 * np.sqrt(np.fabs(lng))
    )
    ret += (20.0 * np.sin(6.0 * lng * pi) + 20.0 * np.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * np.sin(lat * pi) + 40.0 * np.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * np.sin(lat / 12.0 * pi) + 320 * np.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    import numpy as np

    ret = (
        300.0
        + lng
        + 2.0 * lat
        + 0.1 * lng * lng
        + 0.1 * lng * lat
        + 0.1 * np.sqrt(np.abs(lng))
    )
    ret += (20.0 * np.sin(6.0 * lng * pi) + 20.0 * np.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * np.sin(lng * pi) + 40.0 * np.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (
        (150.0 * np.sin(lng / 12.0 * pi) + 300.0 * np.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    )
    return ret


def clean_content(content, place):
    # 去除地名
    content = content.replace(place, "")
    # 去除一些关键词
    content = (
        content.replace("分享图片", "")
        .replace("分享视频", "")
        .replace("微博视频", "")
        .replace("的微博视频", "")
        .replace("网页链接", "")
        .replace("超话", "")
        .replace("新浪图片", "")
        .replace("<br>", "")
    )
    # 去除英文
    content = re.sub(r"[a-zA-Z]+", "", content)
    content = (
        re.sub(r"\d+", "", content).replace(" ", "").replace(".", "").replace("_", "")
    )
    # 去除所有非中文符号
    content = re.sub(r"[^\u4e00-\u9fa5]", "", content)
    # 去除空白字符
    content = re.sub(r"\s+", "", content)
    return content


