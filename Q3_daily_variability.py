# /// script
# dependencies = [
#     "marimo>=0.25.2",
#     "matplotlib==3.11.2",
#     "pandas==3.1.0",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd


    return mo, pd


@app.cell
def _(pd):
    day_df = pd.read_csv("day.csv")
    day_df.head(350)
    # day_df.describe()
    day_df.columns
    return (day_df,)


@app.cell
def _(pd):
    hour_df = pd.read_csv("hour.csv")
    hour_df.head(3500)
    hour_df.describe()
    #hour_df.columns
    return (hour_df,)


@app.cell
def _(hour_df, pd):
    # 1. Convert date column to datetime objects
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

    # 2. Quick statistical check on hourly counts
    hourly_stats = hour_df["cnt"].describe()

    hourly_stats
    return


@app.cell
def _():
    return


@app.cell
def _(hour_df):
    # Aggregate hourly data up to daily totals to answer Q3
    daily_from_hour = (
        hour_df.groupby("dteday")
        .agg({
            "cnt": "sum",
            "casual": "sum",
            "registered": "sum",
            "temp": "mean",
            "hum": "mean",
            "windspeed": "mean",
            "weathersit": "max"
        })
        .reset_index()
    )

    # Sort chronologically
    daily_from_hour = daily_from_hour.sort_values("dteday").reset_index(drop=True)

    # Calculate 21-day rolling median and IQR for anomaly detection
    daily_from_hour["rolling_med"] = daily_from_hour["cnt"].rolling(window=21, center=True, min_periods=7).median()
    daily_from_hour["rolling_q25"] = daily_from_hour["cnt"].rolling(window=21, center=True, min_periods=7).quantile(0.25)
    daily_from_hour["rolling_q75"] = daily_from_hour["cnt"].rolling(window=21, center=True, min_periods=7).quantile(0.75)

    # Statistical Summary via .describe()
    q3_summary = daily_from_hour["cnt"].describe()

    q3_summary
    return


@app.cell
def _(day_df, mo, plt):
    import matplotlib.dates as mdates

    # 1. Create a clean, wide canvas
    fig, ax = plt.subplots(figsize=(10, 5.5))

    # 2. Pick professional, colorblind-friendly colors
    col_2011 = "#0072B2"  # Blue
    col_2012 = "#D55E00"  # Orange-Red

    # 3. Plot the two years overlapping
    ax.hist(day_df.loc[day_df["yr"] == 0, "cnt"], bins=20, alpha=0.65, 
            color=col_2011, edgecolor="white", label="2011 (Mean: ~3,400)")
    ax.hist(day_df.loc[day_df["yr"] == 1, "cnt"], bins=20, alpha=0.65, 
            color=col_2012, edgecolor="white", label="2012 (Mean: ~5,600)")

    # 4. Clean up the design
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    # 5. Add clear labels
    ax.set_title("Variability of Daily Bike Rentals (2011 vs. 2012)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Daily Total Bike Rentals [count]", fontsize=11)
    ax.set_ylabel("Number of Days", fontsize=11)
    ax.legend(frameon=False, fontsize=10)

    # 6. Display the chart in marimo (passing 'ax' instead of 'fig')
    chart1 = mo.ui.matplotlib(ax)
    chart1
    return


@app.cell
def _():
    import matplotlib.pyplot as plt

    return (plt,)


@app.cell
def _(mo):
    # Create an interactive dropdown for Season
    season_dropdown = mo.ui.dropdown(
        options={
            "All Seasons": 0,
            "1: Winter/Early Spring": 1,
            "2: Spring/Early Summer": 2,
            "3: Summer/Early Fall": 3,
            "4: Late Fall/Early Winter": 4,
        },
        value="All Seasons",  # Fixed: matches the dictionary key
        label="Select Season Filter:"
    )

    # Create an interactive slider for filtering minimum total rentals
    slider_min_cnt = mo.ui.slider(
        start=0, 
        stop=8000, 
        step=500, 
        value=0, 
        label="Filter Days with Minimum Rentals:"
    )

    # Display them interactively in the browser
    mo.hstack([season_dropdown, slider_min_cnt])
    return


if __name__ == "__main__":
    app.run()
