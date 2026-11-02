import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", layout_file="layouts/q4_weather.slides.json")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # **How is rental activity associated with weather?**
    ---
    Question 4: weather and bike-sharing activity. Capital Bikeshare, Washington D.C., 2011 and 2012. Data: UCI Bike Sharing dataset (Fanaee-T, 2013).
    """)
    return


@app.cell
def _():
    # Import some libraries
    # ---------------------
    import pandas as pd
    import matplotlib.pyplot as plt

    # same colours and chart style as question 1
    YEAR_COLORS = {2011: "#1f77b4", 2012: "#d95f02"}
    plt.rcParams.update({
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": "gray", "grid.linestyle": "--", "grid.linewidth": 0.5,
        "axes.titlesize": 30, "axes.titlepad": 20, "figure.titlesize": 30,
        "axes.labelsize": 20, "axes.labelpad": 20,
        "xtick.labelsize": 20, "ytick.labelsize": 20, "legend.fontsize": 20,
    })
    return YEAR_COLORS, pd, plt


@app.cell(hide_code=True)
def _(day, mo):
    mo.md(f"""
    ## **EDA**

    We plot each weather variable in day.csv against the number of rentals per day (cnt), one dot per day for all {len(day)} days. The colours show the year, because 2012 is much busier than 2011. The weather is stored on a 0 to 1 scale, so for the plots we convert it back with the formulas from the UCI page: temperature -8 + 47 * temp, felt temperature -16 + 66 * atemp, humidity 100 * hum and wind 67 * windspeed (the wind unit is not documented). Nothing in the data is changed or removed.
    """)
    return


@app.cell
def _(pd):
    # Read data
    # ---------
    # the daily file as it comes from UCI
    day = pd.read_csv("day.csv", parse_dates=["dteday"])
    year = 2011 + day["yr"]
    return day, year


@app.cell(hide_code=True)
def _(hour_check, mo):
    mo.md(f"""
    ### ***day.csv or hour.csv?***

    day.csv is hour.csv added up per day. On all {hour_check['days where cnt = sum of the hours']} days the daily count is the sum of the hourly counts, and the daily weather is the mean of the recorded hours (the largest difference is {hour_check['largest difference in the weather columns']}, just rounding). Our question is about weather and rentals per day, so day.csv is enough. The hourly file would mostly add the time of day, like the commuting peaks, and that is not weather.

    What we give up: hour.csv misses {hour_check['missing hours']} hours, so {hour_check['days with fewer than 24 hours']} daily totals cover fewer than 24 hours, and one weather code per day hides changes within the day ({hour_check['clear or misty days with a rain hour']} of the {hour_check['clear or misty days']} clear or misty days have at least one hour of rain or snow).
    """)
    return


@app.cell
def _(day, pd):
    # add hour.csv up per day and compare it with day.csv
    _hour = pd.read_csv("hour.csv", parse_dates=["dteday"])
    _daily = _hour.groupby("dteday").agg(
        hours=("hr", "size"), cnt=("cnt", "sum"), rain_hours=("weathersit", lambda s: (s >= 3).sum()),
        temp=("temp", "mean"), atemp=("atemp", "mean"), hum=("hum", "mean"), windspeed=("windspeed", "mean"),
    )
    _day = day.set_index("dteday")
    _weather = ["temp", "atemp", "hum", "windspeed"]
    hour_check = pd.Series({
        "days in day.csv": len(day),
        "days where cnt = sum of the hours": int((_daily["cnt"] == _day["cnt"]).sum()),
        "largest difference in the weather columns": f"{(_daily[_weather] - _day[_weather]).abs().max().max():.0e}",
        "missing hours": 24 * len(day) - len(_hour),
        "days with fewer than 24 hours": int((_daily["hours"] < 24).sum()),
        "hours recorded on 2012-10-29": int(_daily.loc["2012-10-29", "hours"]),
        "clear or misty days": int((_day["weathersit"] <= 2).sum()),
        "clear or misty days with a rain hour": int(((_day["weathersit"] <= 2) & (_daily["rain_hours"] > 0)).sum()),
    }, dtype=object)
    hour_check
    return (hour_check,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ***The variables one by one***

    First the plain numbers for each variable, in the same units as the plots: °C, % and wind as 67 * windspeed.
    """)
    return


@app.cell
def _(day, year):
    # rentals per day, for each year
    day.groupby(year.rename("year"))["cnt"].agg(["mean", "median", "std", "min", "max"]).round().astype(int)
    return


@app.cell
def _(day):
    # measured temperature in °C
    (-8 + 47 * day["temp"]).agg(["mean", "median", "std", "min", "max"]).round(1)
    return


@app.cell
def _(day):
    # felt temperature in °C
    (-16 + 66 * day["atemp"]).agg(["mean", "median", "std", "min", "max"]).round(1)
    return


@app.cell
def _(day):
    # relative humidity in %
    (100 * day["hum"]).agg(["mean", "median", "std", "min", "max"]).round(1)
    return


@app.cell
def _(day):
    # wind speed (67 * windspeed, the unit is not documented)
    (67 * day["windspeed"]).agg(["mean", "median", "std", "min", "max"]).round(1)
    return


@app.cell
def _(day, pd):
    # days per weather code: 1 clear, 2 mist, 3 light rain or snow, 4 heavy rain
    _days = day["weathersit"].value_counts().reindex([1, 2, 3, 4], fill_value=0)
    pd.DataFrame({"days": _days, "share (%)": (100 * _days / len(day)).round(1)})
    return


@app.cell
def _(day, pd):
    # days that stand out: humidity 0, felt temperature far from the measured one, almost no rentals
    _temp, _atemp = -8 + 47 * day["temp"], -16 + 66 * day["atemp"]
    _odd = (day["hum"] == 0) | ((_atemp - _temp).abs() > 15) | (day["cnt"] < 100)
    pd.DataFrame({
        "date": day["dteday"].dt.date, "temp (°C)": _temp.round(1),
        "atemp (°C)": _atemp.round(1) + 0.0,  # + 0.0 shows -0.0 as 0.0
        "humidity (%)": (100 * day["hum"]).round(1), "weathersit": day["weathersit"], "cnt": day["cnt"],
    })[_odd]
    return


@app.cell(hide_code=True)
def _(day, hour_check, mo, year):
    _mean = day.groupby(year)["cnt"].mean()
    _rain = day["weathersit"] == 3
    _sandy = day.loc[day["dteday"] == "2012-10-29", "cnt"].iloc[0]
    _august = -8 + 47 * day.loc[day["dteday"] == "2012-08-17", "temp"].iloc[0]
    mo.md(f"""
    ### ***What stands out***

    - 2012 is much busier than 2011: {_mean[2012]:,.0f} rentals on an average day against {_mean[2011]:,.0f} ({_mean[2012] / _mean[2011] - 1:+.0%}). That is why the plots show the two years in different colours.
    - Humidity is 0 on 10 March 2011, which cannot be right. We keep the day but do not trust that value.
    - On 17 August 2012 the felt temperature is about 0 °C while the measured one is {_august:.0f} °C, most likely a recording error.
    - 29 October 2012 has only {_sandy} rentals, because hour.csv has just {hour_check['hours recorded on 2012-10-29']} recorded hour that day (Hurricane Sandy).
    - Weather code 4 (heavy rain) never shows up in day.csv, and light rain or snow covers only {_rain.sum()} days, {(_rain & (year == 2012)).sum()} of them in 2012.
    """)
    return


@app.cell
def _(YEAR_COLORS, day, mo, plt, year):
    _temps = {
        "Measured temperature (temp)": -8 + 47 * day["temp"],
        "Felt temperature (atemp)": -16 + 66 * day["atemp"],
    }
    _fig, _axes = plt.subplots(1, 2, figsize=(18, 9), sharex=True, sharey=True)
    for _ax, (_name, _t) in zip(_axes, _temps.items()):
        for _y, _color in YEAR_COLORS.items():
            _ax.scatter(_t[year == _y], day.loc[year == _y, "cnt"], s=30, color=_color,
                        alpha=0.6, linewidths=0, label=str(_y))
        _ax.set_title(_name, fontsize=20)
        _ax.set_xlabel("°C")
    _axes[0].set_ylabel("Rentals per day")
    _axes[0].legend(loc="upper left", markerscale=2)
    _fig.suptitle("Temperature and daily bike rentals")
    _fig.tight_layout()
    plt.close(_fig)
    mo.center(_fig)
    return


@app.cell
def _(YEAR_COLORS, day, mo, plt, year):
    _hum = 100 * day["hum"]
    _fig, _ax = plt.subplots(figsize=(12, 9))
    for _y, _color in YEAR_COLORS.items():
        _ax.scatter(_hum[year == _y], day.loc[year == _y, "cnt"], s=30, color=_color,
                    alpha=0.6, linewidths=0, label=str(_y))
    _ax.set(title="Humidity and daily bike rentals", xlabel="Relative humidity (%)", ylabel="Rentals per day")
    _ax.legend(loc="upper left", markerscale=2)
    _fig.tight_layout()
    plt.close(_fig)
    mo.center(_fig)
    return


@app.cell
def _(YEAR_COLORS, day, mo, plt, year):
    _wind = 67 * day["windspeed"]
    _fig, _ax = plt.subplots(figsize=(12, 9))
    for _y, _color in YEAR_COLORS.items():
        _ax.scatter(_wind[year == _y], day.loc[year == _y, "cnt"], s=30, color=_color,
                    alpha=0.6, linewidths=0, label=str(_y))
    _ax.set(title="Wind and daily bike rentals", xlabel="Wind speed",
            ylabel="Rentals per day")
    _ax.legend(loc="upper right", markerscale=2)
    _fig.tight_layout()
    plt.close(_fig)
    mo.center(_fig)
    return


@app.cell
def _(day, mo, plt, year):
    # day.csv only has codes 1 to 3, code 4 (heavy rain) only shows up in a few hours of hour.csv
    _codes = {1: "Clear / partly cloudy", 2: "Mist / cloudy", 3: "Light rain / snow"}
    # box style of question 1, with a pale fill per year (2011 blue, 2012 orange)
    _fills = {2011: ("#dbeafe", "#4b78a8"), 2012: ("#fde0c5", "#d95f02")}
    _fig, _ax = plt.subplots(figsize=(12, 9))
    _ticks = []
    for _i, (_code, _label) in enumerate(_codes.items()):
        _n = []
        for _shift, (_y, (_face, _edge)) in zip((-0.19, 0.19), _fills.items()):
            _values = day.loc[(day["weathersit"] == _code) & (year == _y), "cnt"]
            _n.append(len(_values))
            _ax.boxplot(_values, positions=[_i + _shift], widths=0.32, patch_artist=True, showmeans=True,
                        boxprops={"facecolor": _face, "edgecolor": _edge},
                        meanprops={"marker": "D", "markerfacecolor": "#d95f02", "markeredgecolor": "white",
                                   "markersize": 7},
                        medianprops={"color": "#1f2937", "linewidth": 2},
                        whiskerprops={"color": "#64748b"}, capprops={"color": "#64748b"},
                        flierprops={"marker": "o", "markerfacecolor": "#94a3b8", "markeredgecolor": "none",
                                    "markersize": 4, "alpha": 0.6})
        _ticks.append(f"{_label}")
    _ax.set_xticks(range(len(_codes)), _ticks)
    _ax.set_xlim(-0.6, len(_codes) - 0.4)
    _ax.grid(axis="x", visible=False)
    for _y, (_face, _edge) in _fills.items():
        _ax.scatter([], [], marker="s", s=200, facecolor=_face, edgecolor=_edge, label=str(_y))
    _ax.legend(loc="upper right")
    _ax.set(title="Weather category and daily bike rentals", ylabel="Rentals per day",
            xlabel="Weather category")
    _fig.tight_layout()
    plt.close(_fig)
    mo.center(_fig)
    return


if __name__ == "__main__":
    app.run()
