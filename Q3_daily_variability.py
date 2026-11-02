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


@app.cell(hide_code=True)
def _(pd):
    day_df = pd.read_csv("day.csv")
    day_df.head(350)
    # day_df.describe()
    #day_df.columns
    return (day_df,)


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    By removing the raw numerical text and transitioning to a continuous Yellow-Green-Blue (YlGnBu) color palette, this day-of-the-month heatmap leverages the human eye's natural ability to instantly process intensity over reading numbers. The Y-axis maps the macro-level progression of the months, while the X-axis captures the granular daily rhythm from the 1st to the 31st. Lighter yellow tiles immediately flag unusually quiet days—exposing severe winter months or sudden mid-month weather disruptions—while deep blue tiles visually cluster to reveal the massive seasonal ridership wave during the summer and early fall. This minimalist design strips away cognitive clutter, allowing reviewers to intuitively spot structural calendar gaps (like the end of February) and specific anomalous dates, all while using the interactive toggle to see how these exact behavioral patterns scaled up between 2011 and 2012.
    """)
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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
        mo.md("### Calendar Heatmap (Day of the Month)\n"
              "The color gradient makes seasonal waves and sudden drops easy to spot at a glance."),
        year_selector,
        fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    group_dropdown = mo.ui.dropdown(
        options={
            "By Month": "mnth",
            "By Season": "season",
            "By Day of the Week": "weekday",
        },
        value="By Day of the Week",
        label="Group boxplots by:",
    )
    group_dropdown
    return (group_dropdown,)


@app.cell(hide_code=True)
def _(day_df, group_dropdown, mo, plt):
    _LMU_GREEN = "#00883A"   # official LMU green
    _DARK_GREY = "#333333"

    # Tick labels for each grouping option
    _LABELS = {
        "mnth": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "season": ["Winter", "Spring", "Summer", "Fall"],
        "weekday": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],  # dataset: 0 = Sunday
    }

    _column = group_dropdown.value
    _rentals_by_group = [
        _group["cnt"].dropna().values
        for _, _group in day_df.groupby(_column)   # groups come out sorted
    ]

    _fig, _ax = plt.subplots(figsize=(9.5, 4.8))
    _ax.boxplot(
        _rentals_by_group,
        patch_artist=True,
        boxprops=dict(facecolor=_LMU_GREEN, alpha=0.75, edgecolor=_DARK_GREY),
        medianprops=dict(color="black", linewidth=2),
        whiskerprops=dict(color=_DARK_GREY),
        capprops=dict(color=_DARK_GREY),
        flierprops=dict(marker="D", markersize=5, markerfacecolor=_DARK_GREY,
                        markeredgecolor="white", alpha=0.8),
    )

    _ax.set_xticks(range(1, len(_rentals_by_group) + 1), labels=_LABELS[_column])
    _ax.set_ylabel("Daily Total Bike Rentals")
    _ax.set_title(
        f"Rental Variability & Outliers {group_dropdown.selected_key.lower()}",
        fontweight="bold", pad=12,
    )
    _ax.spines[["top", "right"]].set_visible(False)
    _ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.close(_fig)  # prevents the figure from rendering twice

    mo.vstack([
        mo.md("### Interactive Conditional Boxplots\n"
              "Use the dropdown to compare how rentals vary across groups. "
              "The dark diamonds are unusual days (beyond 1.5 × IQR from the box)."),
        group_dropdown,
        _fig,
    ])
    return


if __name__ == "__main__":
    app.run()
