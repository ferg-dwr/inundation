"""Calculate Yolo Bypass inundation duration and presence.

This module contains the main function that calculates inundation metrics
by combining Fremont Weir stage height data with Dayflow data.

An inundation event occurs when water from the Sacramento River overflows
into the Yolo Bypass, typically during high flow periods.
"""

import pandas as pd

from .dayflow import get_dayflow
from .fremont import get_fre


def calc_inundation() -> pd.DataFrame:
    """Calculate Yolo Bypass inundation duration and presence.

    Downloads all available Fremont Weir and Dayflow data, merges them,
    and calculates the number of inundation days and whether inundation
    is occurring each day.

    Returns
    -------
    pd.DataFrame
        DataFrame with daily inundation data from 1984-present, including:
        - date : datetime64[ns]
            Date of observation
        - sac : float
            Sacramento River flow (dayflow, cubic feet per day)
        - yolo : float
            Yolo Bypass flow (dayflow, cubic feet per day)
        - yolo_dayflow : float
            Yolo Bypass flow (dayflow, cubic feet per day) - renamed column
        - height_sac : float
            Sacramento River stage height (feet, Fremont Weir)
        - inund_days : int
            Cumulative inundation days since event started
        - inundation : int
            Binary indicator: 1 = inundation occurring, 0 = no inundation

    Examples
    --------
    >>> inun = calc_inundation()
    >>> print(inun.head())
    >>> print(f"Total inundation events: {inun['inundation'].sum()}")

    Notes
    -----
    Inundation thresholds vary by date due to datum changes:
    - Before October 3, 2016: height_sac ≥ 33.5 feet
    - After October 3, 2016: height_sac ≥ 32.0 feet

    The calculation begins February 1, 1984 because an inundation event had
    already begun when Fremont Weir measurements started (mid-November 1983).

    Data quality: Years 1989-1991 contain four days with potentially suspect
    Fremont Weir values that require further investigation.

    See Also
    --------
    get_fre : Download Fremont Weir stage height data
    get_dayflow : Download Dayflow data

    References
    ----------
    - Goertler, C.M., Sommer, T., et al. (2017).
      Ecological patterns of species dominance in Yolo Bypass, California.
      Ecology of Freshwater Fish, 26(3), 415-426.
      https://doi.org/10.1111/eff.12372
    """
    # Download both datasets
    print("Downloading Fremont Weir data...")
    fre = get_fre()

    print("Downloading Dayflow data...")
    dayflow = get_dayflow()

    # Extract date from datetime for FRE data
    fre["date"] = pd.to_datetime(fre["datetime"]).dt.date
    fre["date"] = pd.to_datetime(fre["date"])

    # Quality control: remove unrealistic values (Peak Stage of Record 41.02')
    fre_qc = fre[(fre["value"] > 2) & (fre["value"] < 41.03)].copy()

    # Aggregate hourly data to daily maximum
    discharge_sac = fre_qc.groupby("date")["value"].max().reset_index(name="height_sac")

    # Create continuous date sequence from 1984-02-01 to today
    start_date = pd.Timestamp("1984-02-01")
    end_date = pd.Timestamp.today()
    all_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    continuous_dates = pd.DataFrame({"date": all_dates})

    # Merge to find missing dates and fill with NaN
    discharge_sac_na = continuous_dates.merge(discharge_sac, on="date", how="left")

    # Impute missing values using exponential weighted moving average
    # Using pandas' ewm method as alternative to imputeTS::na_ma
    height_values = discharge_sac_na["height_sac"].copy()
    mask = height_values.isna()

    if mask.any():
        # Use forward fill then backward fill for imputation (pandas 2.x compatible)
        filled = height_values.ffill().bfill()
        # Optionally use exponential weighted mean for smoothing
        discharge_sac_na["height_sac_na"] = filled.ewm(span=7, adjust=False).mean()
    else:
        discharge_sac_na["height_sac_na"] = height_values

    # Prepare dayflow data
    dayflow_clean = dayflow.dropna().copy()
    dayflow_clean["date"] = pd.to_datetime(dayflow_clean["date"]).dt.date
    dayflow_clean["date"] = pd.to_datetime(dayflow_clean["date"])

    # Merge the two datasets
    discharge_sac_na = discharge_sac_na[["date", "height_sac_na"]]
    all_flows = dayflow_clean.merge(discharge_sac_na, on="date", how="inner")

    # Sort by date
    all_flows = all_flows.sort_values("date").reset_index(drop=True)

    # Initialize inundation days column
    all_flows["inund_days"] = 0

    # Rename yolo column for clarity
    if "yolo" in all_flows.columns:
        all_flows = all_flows.rename(columns={"yolo": "yolo_dayflow"})

    # Calculate inundation days based on stage height thresholds
    # Thresholds changed on October 3, 2016 due to datum shift
    threshold_date = pd.Timestamp("2016-10-03")
    threshold_before = 33.5  # feet
    threshold_after = 32.0  # feet

    for i in range(len(all_flows)):
        date = all_flows.loc[i, "date"]
        height = all_flows.loc[i, "height_sac_na"]

        # Determine which threshold to use
        threshold = threshold_before if date < threshold_date else threshold_after

        # Check if water is high enough for inundation
        if height >= threshold:
            if i == 0:
                all_flows.loc[i, "inund_days"] = 1
            else:
                all_flows.loc[i, "inund_days"] = all_flows.loc[i - 1, "inund_days"] + 1
        else:
            all_flows.loc[i, "inund_days"] = 0

    # Jessica's addition: fix the tails based on high Yolo flow
    for i in range(1, len(all_flows)):
        yolo_flow = all_flows.loc[i, "yolo_dayflow"]
        prev_inund = all_flows.loc[i - 1, "inund_days"]
        if yolo_flow >= 4000 and prev_inund > 0:
            all_flows.loc[i, "inund_days"] = prev_inund + 1

    # Correct special cases in 1995 and 2019
    for i in range(1, len(all_flows)):
        date = all_flows.loc[i, "date"]
        height = all_flows.loc[i, "height_sac_na"]
        prev_inund = all_flows.loc[i - 1, "inund_days"]
        threshold = threshold_before if date < threshold_date else threshold_after

        if height >= threshold and prev_inund > 0:
            all_flows.loc[i, "inund_days"] = prev_inund + 1

    # Add binary inundation indicator (1 = inundation, 0 = no inundation)
    all_flows["inundation"] = (all_flows["inund_days"] > 0).astype(int)

    # Rename height_sac_na to height_sac for final output
    all_flows = all_flows.rename(columns={"height_sac_na": "height_sac"})

    # Reorder columns for clarity
    column_order = [
        "date",
        "sac",
        "yolo_dayflow",
        "height_sac",
        "inund_days",
        "inundation",
    ]
    all_flows = all_flows[[col for col in column_order if col in all_flows.columns]]

    print("Inundation calculation complete!")
    return all_flows


__all__ = ["calc_inundation"]
