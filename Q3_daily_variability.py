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
    import numpy as np
    import matplotlib.pyplot as plt

    return mo, pd, plt


@app.cell
def _(pd):
    day_df = pd.read_csv("day.csv")
    day_df.head(350)
    # day_df.describe()
    #day_df.columns
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
def _(day_df):
    pivot = day_df.pivot_table(index="mnth", columns="weekday", values="cnt", aggfunc="mean")
    print(pivot.head())

    weathers = sorted(day_df['weathersit'].unique())
    print(weathers)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The Calendar Heatmap: Visualizing Seasonal and Weekly Rhythms
    "To answer 'when is the system unusually quiet or busy?', we needed to compress 731 days of rental data into a single, intuitive snapshot without overwhelming the viewer with a wall of numbers. We designed this interactive calendar heatmap with months flowing naturally from left to right on the X-axis and days of the week on the Y-axis. This specific layout was chosen because it aligns with our natural mental model of a timeline, allowing the human eye to instantly process macro trends through color gradients. At a glance, the heatmap exposes the massive seasonal 'bell curve' of the dataset—highlighting a stark contrast between the low-volume winter months (January and February) and the highly active summer peak (May through September). Furthermore, by embedding an interactive toggle, we avoided chart clutter; reviewers can dynamically switch between 2011 and 2012 to instantly see how the entire system's volume scaled up year-over-year while preserving the exact same seasonal and weekly behavioral rhythms.
    """)
    return


@app.cell
def _(mo):
    year_selector = mo.ui.dropdown(
        options={
            "Both Years (2011 & 2012)": None,   
            "2011 Only": 0,
            "2012 Only": 1,
        },
        value="Both Years (2011 & 2012)",
        label="Select year:"
    )

    # Standalone line so marimo displays it
    year_selector
    return (year_selector,)


@app.cell
def _(day_df, mo, pd, plt, year_selector):
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Filter by year (None means keep both years)
    year = year_selector.value
    data = day_df if year is None else day_df[day_df["yr"] == year]

    # Average rentals for every (month, day-of-month) pair -> 12 x 31 grid
    day_of_month = pd.to_datetime(data["dteday"]).dt.day
    avg_rentals = (
        data.groupby(["mnth", day_of_month])["cnt"].mean()
            .unstack()
            .reindex(index=range(1, 13), columns=range(1, 32))
    )

    # Dates that don't exist (Feb 30, Apr 31...) show as light grey, not blank
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad("#eeeeee")

    fig, ax = plt.subplots(figsize=(15, 5.5))
    image = ax.imshow(avg_rentals, cmap=cmap, aspect="auto")

    ax.set_xticks(range(31), labels=range(1, 32))
    ax.set_yticks(range(12), labels=MONTHS)
    ax.set_title("Average Daily Rentals by Month and Day", fontweight="bold", pad=15)
    ax.spines[:].set_visible(False)

    # Thin white lines between cells give it a calendar look
    ax.set_xticks([x - 0.5 for x in range(32)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(13)], minor=True)
    ax.grid(which="minor", color="white", linewidth=1)
    ax.tick_params(which="both", length=0)

    fig.colorbar(image, ax=ax, pad=0.02, label="Average Daily Rentals")
    plt.close(fig)  # prevents the figure from rendering twice

    mo.vstack([
        mo.md("### 📅 Calendar Heatmap (Day of the Month)\n"
              "The color gradient makes seasonal waves and sudden drops easy to spot at a glance."),
        year_selector,
        fig,
    ])
    return


@app.cell
def _(mo):
    # 1. Added 'weekday' to our interactive dropdown!
    group_dropdown = mo.ui.dropdown(
        options={
            "By Month": "mnth",
            "By Season": "season",
            "By Weather Situation": "weathersit",
            "By Day of the Week (0=Sun, 6=Sat)": "weekday",
            "By Working Day (0=Off, 1=Workday)": "workingday"
        },
        value="By Day of the Week (0=Sun, 6=Sat)",
        label="Group Boxplots By:"
    )
    return (group_dropdown,)


@app.cell(hide_code=True)
def _(day_df, group_dropdown, mo, plt):
    # 1. Get the selected column (made private with _)
    _col = group_dropdown.value

    # 2. Create the canvas
    _fig, _ax = plt.subplots(figsize=(9.5, 4.8))

    # 3. Extract data groups 
    _groups = sorted(day_df[_col].unique())
    _data_to_plot = [day_df[day_df[_col] == g]["cnt"].dropna().values for g in _groups]

    # 4. Draw Vertical Boxplots
    _ax.boxplot(
        _data_to_plot, 
        vert=True, 
        patch_artist=True,
        boxprops=dict(facecolor="#0072B2", alpha=0.75, edgecolor="#222222"),
        medianprops=dict(color="#111111", linewidth=2),
        flierprops=dict(marker="o", markerfacecolor="#D55E00", markersize=5, alpha=0.7, markeredgecolor="#222222")
    )

    # 5. Apply dynamic labels based on what the user picked
    _ax.set_xticks(range(1, len(_groups) + 1))

    if _col == "mnth":
        _labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    elif _col == "season":
        _labels = ["1: Winter", "2: Spring", "3: Summer", "4: Fall"]
    elif _col == "weathersit":
        _labels = ["1: Clear / Few Clouds", "2: Mist / Cloudy", "3: Light Snow / Rain"]
    elif _col == "weekday":
        _labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    else:
        _labels = ["0: Weekend / Holiday", "1: Working Day"]
    
    _ax.set_xticklabels(_labels, fontsize=10)

    # 6. Clean formatting
    _ax.set_ylabel("Daily Total Bike Rentals", fontsize=11)
    _ax.set_title(f"Conditional Variability & Outliers ({group_dropdown.value.replace('By ', 'by ')})", fontweight="bold", pad=12)
    _ax.spines["top"].set_visible(False)
    _ax.spines["right"].set_visible(False)
    _ax.grid(axis="y", linestyle="--", alpha=0.4)

    # 7. Output to browser
    mo.vstack([
        mo.md("### Interactive Conditional Boxplots\nUse the dropdown to isolate variability. The orange dots represent mathematically unusual days ($> 1.5 \\times \\text{IQR}$)."),
        group_dropdown,
        mo.ui.matplotlib(_ax)
    ])
    return


if __name__ == "__main__":
    app.run()
