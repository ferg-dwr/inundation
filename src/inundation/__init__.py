"""Inundation: Calculate Yolo Bypass inundation duration.

A Python package for downloading and calculating statistics related to
Yolo Bypass inundation duration.

The package downloads and processes data from two sources:
- CDEC Fremont Weir data: Sacramento River stage height
- Dayflow data: Modeled flow of Sacramento River and Yolo Bypass

Main Functions
--------------
get_fre : Download Fremont Weir stage height data
get_dayflow : Download Dayflow data
calc_inundation : Calculate inundation duration and presence

Cache Management
----------------
show_cache : Show list of cached files
clear_cache : Remove all cached files

Examples
--------
Calculate inundation:

>>> from inundation import calc_inundation
>>> inun = calc_inundation()
>>> print(inun.head())

Access individual datasets:

>>> from inundation import get_fre, get_dayflow
>>> fre = get_fre()
>>> dayflow = get_dayflow()

References
----------
Original research: Goertler et al. (2017)
https://onlinelibrary.wiley.com/doi/10.1111/eff.12372

Data sources:
- CDEC: https://cdec.water.ca.gov/
- Dayflow: https://data.cnra.ca.gov/dataset/dayflow
"""

__version__ = "0.1.0"
__author__ = "Christopher M. Goertler"
__email__ = "cmgoertler@ucdavis.edu"

from .cache import clear_cache, show_cache
from .dayflow import get_dayflow
from .fremont import get_fre
from .inundation import calc_inundation

__all__ = [
    "get_fre",
    "get_dayflow",
    "calc_inundation",
    "show_cache",
    "clear_cache",
    "__version__",
]
