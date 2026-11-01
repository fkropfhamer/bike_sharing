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
    # Weather and bike-sharing activity

    ### How is rental activity associated with weather?

    Question 4, Capital Bikeshare, Washington D.C., 2011 and 2012

    Which differences go with the weather itself, and which only reflect the season? We compare rental events descriptively, with 95% intervals and a few checks of our own choices.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Weather and season move together: warm days are mostly summer days, and summer is busier for many reasons. So we go step by step:

    1. EDA: what is in the data, what is missing, and which settings we use later.
    2. Temperature across the year (finding 1).
    3. Temperature from day to day, with the seasonal level taken out (finding 2).
    4. Rain, mist, humidity and wind, compared with clear hours at the same time (findings 3 and 4).
    5. Casual and registered rentals (finding 5).
    6. Temperature and weather category side by side (finding 6), then the conclusion and the limitations.

    Each step starts with a short note on what we do and why. All numbers in the text are computed from the data.
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import StrMethodFormatter
    import bike_data as bd

    # One shared chart style for the EDA and the findings.
    bd.set_plot_style()
    PAL = bd.PALETTE
    thousands = StrMethodFormatter("{x:,.0f}")
    return PAL, bd, np, pd, plt, thousands


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## EDA

    Before the analysis we look at the raw data: what is missing, whether the documentation is right, and how rentals depend on the calendar and the weather. Each step ends with what we decide from it. The decisions are collected in a settings cell, and at the end of the EDA we check that other reasonable settings would not change the conclusions.
    """)
    return


@app.cell(hide_code=True)
def _(hours_per_day, missing, mo, raw_hour):
    _short = hours_per_day[hours_per_day < 22].sort_values()
    _gaps = missing.loc[missing["dteday"].map(hours_per_day) >= 22, "hr"]
    _night = "all" if _gaps.between(1, 6).all() else f"{_gaps.between(1, 6).mean():.0%} of them"
    mo.md(f"""
    ### Missing hours

    hour.csv should have 24 rows for each of the {len(hours_per_day)} days, but {len(missing)} hours have no row. No recorded hour has 0 rentals (the smallest count is {raw_hour['cnt'].min()}), so a missing hour could also be an hour in which nobody rented a bike. We cannot tell, so we leave missing hours missing and never fill in zeros. Since day.csv is just hour.csv added up, a day with missing hours also has an incomplete daily total.

    {len(_short)} days miss 3 or more hours. The worst is {_short.index[0].day} {_short.index[0]:%B %Y} with only {_short.iloc[0]} recorded hour, when Hurricane Sandy hit the region. On the other days the {len(_gaps)} missing hours are {_night} between 1 and 7 am, when hardly anyone rents a bike. So we drop the {len(_short)} days and keep the rest. Asking for all 24 hours would cost {int(hours_per_day.between(22, 23).sum())} more days for very little gain.
    """)
    return


@app.cell
def _(bd, pd):
    raw_day = pd.read_csv(bd.DATA_DIR / "day.csv", parse_dates=["dteday"])
    raw_hour = pd.read_csv(bd.DATA_DIR / "hour.csv", parse_dates=["dteday"])
    hours_per_day = raw_hour.groupby("dteday").size().reindex(raw_day["dteday"], fill_value=0)
    missing = bd.missing_hours()  # one row for every date and hour without a row in hour.csv

    # how many days have how many recorded hours
    hours_per_day.value_counts().sort_index().rename_axis("recorded hours").to_frame("days")
    return hours_per_day, missing, raw_day, raw_hour


@app.cell(hide_code=True)
def _(formula_check, mo, raw_day):
    _changes = list(raw_day.loc[raw_day["season"].diff() != 0, "dteday"].iloc[1:5])
    _dates = ", ".join(f"{_d.day} {_d:%B}" for _d in _changes[:-1]) + f" and {_changes[-1].day} {_changes[-1]:%B}"
    _readme, _uci = formula_check.iloc[0], formula_check.iloc[1]
    mo.md(f"""
    ### Temperature formula and season labels

    The Readme and the UCI page disagree on two things. The Readme says temp was divided by 41, the UCI page says temp = (t + 8) / 47. With the Readme formula the coldest hour of two Washington winters would be {_readme['coldest hour']:+.1f} °C, which is not realistic. The UCI formula gives {_uci['coldest hour']:.1f} °C and {_uci['hours below 0 °C']:.0f} hours below zero. The season code changes on {_dates}, so code 1 is winter as on the UCI page, not spring as in the Readme. We use the UCI version for both.
    """)
    return


@app.cell
def _(pd, raw_hour):
    # coldest and warmest hour with each temperature formula
    _formulas = {"Readme: 41 * temp": 41 * raw_hour["temp"], "UCI: -8 + 47 * temp": -8 + 47 * raw_hour["temp"]}
    formula_check = pd.DataFrame({
        "coldest hour": {_name: _t.min() for _name, _t in _formulas.items()},
        "warmest hour": {_name: _t.max() for _name, _t in _formulas.items()},
        "hours below 0 °C": {_name: int((_t < 0).sum()) for _name, _t in _formulas.items()},
    })
    formula_check.round(1)
    return (formula_check,)


@app.cell(hide_code=True)
def _(bd, day, mo, odd_days, raw_hour):
    _hum = odd_days[odd_days["hum_zero_hours"] > 0].iloc[0]
    _hum_day = odd_days[odd_days["hum_zero_hours"] > 0].index[0]
    _all = "all " if _hum["hum_zero_hours"] == _hum["hours"] else ""
    _stuck = " and ".join(f"{_d.day} {_d:%B %Y}" for _d in odd_days[odd_days["atemp_values"] == 1].index)
    _wind = 67 * raw_hour["windspeed"]
    _example = _wind[_wind.round() == 30].iloc[0]
    mo.md(f"""
    ### Odd values

    On {_hum_day.day} {_hum_day:%B %Y} humidity is exactly 0 in {_all}{_hum['hum_zero_hours']} recorded hours, which cannot be right, so bike_data.py sets it to missing. The apparent temperature (atemp) does not change all day on {_stuck}, although the temperature does. bike_data.py only masks the August day, but we do not use atemp anyway: it ranks the days almost exactly like the normal temperature (rank correlation {bd.spearman(day['temp_c'], day['atemp_c']):.3f}).

    Wind is stored as whole numbers divided by 67, with small rounding errors (for example {_example:.4f} instead of 30). We round it before putting hours into wind bands, otherwise some hours would land in the wrong band. {(_wind == 0).mean():.1%} of the hours have no wind at all, and we keep them as their own group.
    """)
    return


@app.cell
def _(raw_hour):
    # days where humidity is 0, or atemp stays the same while temp changes
    _days = raw_hour.groupby("dteday").agg(
        hours=("hr", "size"),
        hum_zero_hours=("hum", lambda s: (s == 0).sum()),
        atemp_values=("atemp", "nunique"),
        temp_values=("temp", "nunique"),
    )
    odd_days = _days[(_days["hum_zero_hours"] > 0) | ((_days["atemp_values"] == 1) & (_days["temp_values"] > 1))]
    odd_days
    return (odd_days,)


@app.cell(hide_code=True)
def _(mo, raw_hour):
    mo.md(f"""
    ### Loading the cleaned data

    bike_data.py applies the decisions above: UCI formulas and season labels, the odd humidity and atemp values set to missing, rounded wind, and weather codes 3 and 4 merged into one rain/snow group (code 4 has only {(raw_hour['weathersit'] == 4).sum()} hours). It also checks the files (one row per date and hour, valid codes, counts that add up) and stops with an error if something is wrong. We keep the days with at least 22 recorded hours.
    """)
    return


@app.cell
def _(bd):
    # load both tables with the shared cleaning rules, then drop the days with 3 or more missing hours
    day_all = bd.load_day()
    hour_all = bd.load_hour()
    day = day_all.loc[~day_all["partial_day"]].copy()
    hour = hour_all.loc[~hour_all["partial_day"]].copy()
    return day, day_all, hour, hour_all


@app.cell
def _(day):
    day
    return


@app.cell
def _(hour):
    hour
    return


@app.cell(hide_code=True)
def _(day, hour, mo):
    _means = day.groupby("year")["cnt"].mean()
    _monthly = day.groupby(["year", "mnth"])["cnt"].median().unstack("year")
    _swing = _monthly.max() / _monthly.min()
    _profile = hour.groupby(["workingday", "hr"])["cnt"].mean().unstack("workingday")
    _share = day.groupby("workingday")[["casual", "cnt"]].sum()
    _casual = _share["casual"] / _share["cnt"]
    mo.md(f"""
    ### Calendar patterns

    The calendar moves rentals a lot. 2012 is {_means[2012] / _means[2011] - 1:.0%} busier than 2011, and within a year the busiest month has {_swing.min():.1f} to {_swing.max():.1f} times the rentals of the quietest one. Working days have commuting peaks at {_profile.loc[:11, 1].idxmax()} and {_profile.loc[12:, 1].idxmax()} h, non-working days one broad peak around {_profile[0].idxmax()} h. Casual users make {_casual[0]:.0%} of the rentals on non-working days but only {_casual[1]:.0%} on working days.

    So we split by year, compare hours only with hours of the same month, day type and hour, and give casual and registered rentals their own reference.
    """)
    return


@app.cell
def _(PAL, day, hour, plt):
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(11, 3.4))
    for _year, _color in PAL["year"].items():
        _monthly = day[day["year"] == _year].groupby("mnth")["cnt"].median()
        _left.plot(_monthly.index, _monthly.to_numpy(), marker="o", ms=4, color=_color, label=str(_year))
    _left.set(xlabel="Month", ylabel="Median rentals per day", title="Month and year", xticks=range(1, 13))
    for (_type, _hours), _color in zip(hour.groupby("day_type"), (PAL["context"], PAL["focus"])):
        _profile = _hours.groupby("hr")["cnt"].mean()
        _right.plot(_profile.index, _profile.to_numpy(), color=_color, label=_type)
    _right.set(xlabel="Hour of day", ylabel="Mean rentals per hour", title="Hour and day type", xticks=range(0, 24, 3))
    _left.legend()
    _right.legend()
    _fig.tight_layout()
    plt.close(_fig)  # still shown below, but not kept open
    _fig
    return


@app.cell(hide_code=True)
def _(hour, mo):
    _code = hour["weather3_code"]
    _summer = hour["mnth"].between(6, 8)
    _rain_by_month = (_code == 3).groupby(hour["mnth"]).mean()
    _humidity = hour.groupby("weather3_code")["hum_pct"].median()
    mo.md(f"""
    ### When is the weather bad?

    Mist is more common in the late morning than in the evening ({(_code[hour['hr'].between(8, 12)] == 2).mean():.0%} vs {(_code[hour['hr'].between(17, 21)] == 2).mean():.0%} of the hours) and more common outside summer ({(_code[~_summer] == 2).mean():.0%} vs {(_code[_summer] == 2).mean():.0%}). Rain is spread more evenly, {_rain_by_month.min():.0%} to {_rain_by_month.max():.0%} of the hours in every month. So a plain mist vs clear comparison would partly compare different times of day and year, which is why finding 3 compares hours at the same time.

    Rain hours are also much more humid than clear hours (median {_humidity[3]:.0f}% vs {_humidity[1]:.0f}%), so for humidity and wind we also look at clear hours alone (finding 4).
    """)
    return


@app.cell
def _(PAL, bd, hour, pd, plt):
    _fig, _axes = plt.subplots(1, 2, figsize=(11, 3.2), sharey=True)
    for _ax, _by, _label in [(_axes[0], "mnth", "Month"), (_axes[1], "hr", "Hour of day")]:
        _share = 100 * pd.crosstab(hour[_by], hour["weather3_code"], normalize="index")
        for _code, _color in [(2, PAL["context"]), (3, PAL["focus"])]:
            _ax.plot(_share.index, _share[_code], marker="o", ms=4, color=_color, label=bd.WEATHER3_LABELS[_code])
        _ax.set(xlabel=_label, ylim=(0, None))
    _axes[0].set(ylabel="Share of recorded hours (%)", title="Bad weather by month", xticks=range(1, 13))
    _axes[1].set(title="Bad weather by hour of day", xticks=range(0, 24, 3))
    _axes[0].legend()
    _fig.tight_layout()
    plt.close(_fig)
    _fig
    return


@app.cell
def _(np):
    # Settings used in the analysis. The checks below try other values for each of them.
    MATCH_KEYS = ["year", "mnth", "workingday", "hr"]  # compare hours of the same year, month, day type and hour
    TEMP_EDGES = np.arange(-6, 36, 3)  # 3 °C bands from -6 to 33 °C
    WINDOW_DAYS = 10  # day-to-day baseline: the other days of the same year, at most 10 days away
    BLOCK_DAYS, N_BOOT, SEED = 7, 1000, 2026  # 95% intervals: resample whole weeks, 1000 times
    CLEAR, MIST, RAIN = "Clear / partly cloudy", "Mist / cloudy", "Rain / snow"
    # humidity bands (101 so that 100% is included) and rounded wind bands (no wind is its own band)
    HUM_EDGES, HUM_LABELS = [0, 40, 55, 70, 85, 101], ["<40", "40-54", "55-69", "70-84", "85+"]
    WIND_EDGES, WIND_LABELS = [-0.5, 0.5, 10, 20, 30, 70], ["0", "6-10", "11-20", "21-30", "31+"]
    return (
        BLOCK_DAYS,
        CLEAR,
        HUM_EDGES,
        HUM_LABELS,
        MATCH_KEYS,
        MIST,
        N_BOOT,
        RAIN,
        SEED,
        TEMP_EDGES,
        WINDOW_DAYS,
        WIND_EDGES,
        WIND_LABELS,
    )


@app.cell(hide_code=True)
def _(matching_check, mo):
    _m = matching_check.set_index("matched on")
    _chosen = "year, month, day type, hour"
    _change = abs(_m.loc[_chosen + " (at least 5)", "rain/snow"] - _m.loc[_chosen, "rain/snow"])
    mo.md(f"""
    ### Checking our settings

    Some settings are our own choice. For each one we try a few other values and check whether the conclusion changes.

    #### Matching

    If we match only on year and hour, misty hours reach {_m.loc['year, hour', 'mist']:.2f} of the clear-weather expectation. With month and day type it is {_m.loc[_chosen, 'mist']:.2f}, because misty hours fall at quieter times. Rain stays at about {_m.loc[_chosen, 'rain/snow']:.2f} either way. Adding the weekday would leave only {_m.loc[_chosen + ', weekday', 'rain hours compared (%)']:.0f}% of the rain hours with enough clear hours to compare. So we match on year, month, day type and hour and need at least 3 clear hours (with 5 the rain ratio moves by only {_change:.3f}).
    """)
    return


@app.cell
def _(hour, pd):
    # observed / expected rentals for mist and rain with different ways of matching hours
    _rules = [
        ("year, hour", ["year", "hr"], 3),
        ("year, month, day type, hour", ["year", "mnth", "workingday", "hr"], 3),
        ("year, month, day type, hour (at least 5)", ["year", "mnth", "workingday", "hr"], 5),
        ("year, month, day type, hour, weekday", ["year", "mnth", "workingday", "hr", "weekday"], 3),
    ]
    _rows = []
    for _label, _keys, _minimum in _rules:
        _reference = hour[hour["weather3_code"] == 1].groupby(_keys)["cnt"].agg(expected="mean", n_clear="size")
        _hours = hour.join(_reference, on=_keys)
        _hours = _hours[_hours["n_clear"] >= _minimum]
        _mist, _rain = _hours[_hours["weather3_code"] == 2], _hours[_hours["weather3_code"] == 3]
        _rows.append({
            "matched on": _label,
            "rain hours compared (%)": 100 * len(_rain) / (hour["weather3_code"] == 3).sum(),
            "mist": _mist["cnt"].sum() / _mist["expected"].sum(),
            "rain/snow": _rain["cnt"].sum() / _rain["expected"].sum(),
        })
    matching_check = pd.DataFrame(_rows)
    matching_check.round(3)
    return (matching_check,)


@app.cell(hide_code=True)
def _(band_check, mo):
    _three = band_check.set_index("width (°C)").loc[3]
    _cold = band_check[["below 6 °C vs busiest band, 2011", "below 6 °C vs busiest band, 2012"]]
    mo.md(f"""
    #### Temperature bands

    For finding 1 we tried bands of 2 to 5 °C. With 3 °C only {int(_three['bands under 5 days, 2011'] + _three['bands under 5 days, 2012'])} band has fewer than 5 days, and for every width a day below 6 °C has about {_cold.min().min():.0%} to {_cold.max().max():.0%} of the rentals of the busiest band. The result does not depend on the width, so we use 3 °C bands starting at -6 °C.
    """)
    return


@app.cell
def _(day, np, pd):
    # median day per temperature band for several band widths, separately for each year
    _rows = []
    for _width in (2, 3, 4, 5):
        _edges = np.arange(-6, 36 + _width, _width)
        _row = {"width (°C)": _width}
        for _year, _days in day.groupby("year"):
            _bands = _days.groupby(pd.cut(_days["temp_c"], _edges, right=False), observed=True)["cnt"].agg(["median", "size"])
            _peak = _bands.loc[_bands["size"] >= 10, "median"].max()  # busiest band with at least 10 days
            _row[f"bands under 5 days, {_year}"] = int((_bands["size"] < 5).sum())
            _row[f"below 6 °C vs busiest band, {_year}"] = _days.loc[_days["temp_c"] < 6, "cnt"].median() / _peak
        _rows.append(_row)
    band_check = pd.DataFrame(_rows)
    band_check.round(3)
    return (band_check,)


@app.cell(hide_code=True)
def _(cutoff_check, mo):
    _gap = 1 - cutoff_check.set_index("top band")["observed / expected"]
    mo.md(f"""
    #### Humidity and wind bands

    In finding 4 the interesting part is the top band in clear weather. For humidity the gap stays small wherever the top band starts: {_gap['humidity 80+']:.0%}, {_gap['humidity 85+']:.0%} and {_gap['humidity 90+']:.0%} fewer rentals when it starts at 80, 85 or 90%. For wind it grows with the cut: {_gap['wind above 25']:.0%} fewer rentals above 25, {_gap['wind above 30']:.0%} above 30 and {_gap['wind above 35']:.0%} above 35. We keep the band above 30 and give this range in finding 4.
    """)
    return


@app.cell
def _(MATCH_KEYS, hour, pd):
    # clear hours only, each compared with the other clear hours of the same year, month, day type and hour
    _clear = hour[hour["weather3_code"] == 1]
    _clear = _clear.join(_clear.groupby(MATCH_KEYS)["cnt"].agg(clear_sum="sum", n_clear="size"), on=MATCH_KEYS)
    _clear = _clear[_clear["n_clear"] >= 3]
    _expected = (_clear["clear_sum"] - _clear["cnt"]) / (_clear["n_clear"] - 1)  # the hour itself is left out
    _top_bands = {
        "humidity 80+": _clear["hum_pct"] >= 80,
        "humidity 85+": _clear["hum_pct"] >= 85,
        "humidity 90+": _clear["hum_pct"] >= 90,
        "wind above 25": _clear["wind_rounded"] > 25,
        "wind above 30": _clear["wind_rounded"] > 30,
        "wind above 35": _clear["wind_rounded"] > 35,
    }
    cutoff_check = pd.DataFrame([
        {"top band": _name, "clear hours": int(_in.sum()),
         "observed / expected": _clear.loc[_in, "cnt"].sum() / _expected[_in].sum()}
        for _name, _in in _top_bands.items()
    ])
    cutoff_check.round(3)
    return (cutoff_check,)


@app.cell(hide_code=True)
def _(mo, window_check):
    _w = window_check.set_index("days each side")
    mo.md(f"""
    #### Day-to-day window

    In finding 2 each day is compared with its neighbours. With 7 days on each side, {_w.loc[7, 'days with fewer than 3 neighbours']} days have fewer than 3 neighbours of the same day type; with 10 days every day has enough. The signs do not depend on the window (winter {_w['winter'].min():+.2f} to {_w['winter'].max():+.2f}, summer {_w['summer'].max():+.2f} to {_w['summer'].min():+.2f}), only the size a little. We use 10 days.
    """)
    return


@app.cell
def _(bd, day, np, pd):
    # the day-to-day correlation of finding 2 for several window widths
    _days = day.sort_values("dteday")
    _dates, _years, _types = _days["dteday"].to_numpy(), _days["year"].to_numpy(), _days["workingday"].to_numpy()
    _counts, _temps = _days["cnt"].to_numpy(dtype=float), _days["temp_c"].to_numpy(dtype=float)
    _rows = []
    for _width in (7, 10, 14, 21):
        _few, _count_dev, _temp_dev = 0, [], []
        for _i in range(len(_days)):
            _gap = np.abs((_dates - _dates[_i]) / np.timedelta64(1, "D"))
            _near = (_gap > 0) & (_gap <= _width) & (_years == _years[_i])
            _peers = _near & (_types == _types[_i])
            _few += _peers.sum() < 3
            _count_dev.append(_counts[_i] / np.median(_counts[_peers]) - 1 if _peers.sum() >= 3 else np.nan)
            _temp_dev.append(_temps[_i] - _temps[_near].mean())
        _dev = _days[["season_name"]].assign(cnt=_count_dev, temp=_temp_dev)
        _row = {"days each side": _width, "days with fewer than 3 neighbours": int(_few),
                "all days": bd.spearman(_dev["temp"], _dev["cnt"])}
        for _season in ("Winter", "Summer"):
            _g = _dev[_dev["season_name"] == _season]
            _row[_season.lower()] = bd.spearman(_g["temp"], _g["cnt"])
        _rows.append(_row)
    window_check = pd.DataFrame(_rows)
    window_check.round(3)
    return (window_check,)


@app.cell(hide_code=True)
def _(lag_check, mo):
    mo.md(f"""
    #### Resampling blocks

    For the 95% intervals we resample days, but neighbouring days are alike. Rentals compared with the clear-weather expectation correlate {lag_check.loc[1, 'rentals vs expected']:.2f} with the day before and only {lag_check.loc[7, 'rentals vs expected']:.2f} with the day a week earlier. The share of rain hours is related only to the previous day ({lag_check.loc[1, 'share of rain hours']:.2f}, then about zero). So we resample whole weeks (7-day blocks within each year), 1,000 times; the seed only makes the run repeatable.
    """)
    return


@app.cell
def _(MATCH_KEYS, day_all, hour, pd):
    # correlation between days that are 1 to 14 days apart (dropped days stay as gaps)
    _reference = hour[hour["weather3_code"] == 1].groupby(MATCH_KEYS)["cnt"].agg(expected="mean", n_clear="size")
    _matched = hour.join(_reference, on=MATCH_KEYS)
    _daily = _matched[_matched["n_clear"] >= 3].groupby("dteday")[["cnt", "expected"]].sum()
    _calendar = pd.date_range(day_all["dteday"].min(), day_all["dteday"].max())
    _series = {
        "rentals vs expected": (_daily["cnt"] / _daily["expected"]).reindex(_calendar),
        "share of rain hours": (hour["weather3_code"] == 3).groupby(hour["dteday"]).mean().reindex(_calendar),
    }
    lag_check = pd.DataFrame(
        {_name: [_s.corr(_s.shift(_lag)) for _lag in range(1, 15)] for _name, _s in _series.items()},
        index=pd.RangeIndex(1, 15, name="days apart"),
    )
    lag_check.round(2)
    return (lag_check,)


@app.cell(hide_code=True)
def _(day, day_all, hour, missing, mo):
    _gaps = missing.loc[missing["dteday"].isin(day["dteday"]), "hr"]
    _night = "all" if _gaps.between(1, 6).all() else f"{_gaps.between(1, 6).mean():.0%}"
    mo.md(f"""
    ## The data: {len(day):,} days and {len(hour):,} recorded hours

    - We keep the days with at least 22 of 24 hours recorded and drop {len(day_all) - len(day)} poorly covered days.
    - {len(_gaps)} hours are still missing on {int((~day['complete_day']).sum())} kept days, {_night} between 1 and 7 am. They stay missing and are never counted as zero rentals.
    - Counts are rental events, not people, and every result is an association, not a causal effect.

    Source: UCI Machine Learning Repository, Bike Sharing dataset (Fanaee-T, 2013).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. Rentals rise with temperature up to about 15 °C, then level off
    """)
    return


@app.cell(hide_code=True)
def _(mo, temp_facts):
    mo.md(f"""
    How does the number of rentals change with temperature over the year? We plot daily rentals against the daily mean temperature, separately for each year because 2012 was {temp_facts['growth'] - 1:.0%} busier than 2011. The lines are medians per 3 °C band, because a median is not pulled by a few extreme days. Bands with fewer than 5 days get no median, and bands with 5 to 9 days are drawn hollow.
    """)
    return


@app.cell
def _(PAL, TEMP_EDGES, bd, day, pd, plt, thousands):
    # median rentals per 3 °C band and year; bands with fewer than 5 days are too noisy to show
    _bands = (
        day.assign(t_band=pd.cut(day["temp_c"], TEMP_EDGES, right=False))
        .groupby(["year", "t_band"], observed=True)["cnt"]
        .agg(median="median", n="size")
        .reset_index()
    )
    _bands["t_mid"] = [band.left + 1.5 for band in _bands["t_band"]]
    _bands = _bands.loc[_bands["n"] >= 5]

    fig_temp, _ax = plt.subplots(figsize=(10.5, 4.05))
    _ax.axvspan(15, 30, color=PAL["grid"], alpha=0.45, lw=0, zorder=0)
    _ax.text(22.5, 0.98, "Plateau: 15-30 °C", transform=_ax.get_xaxis_transform(),
             ha="center", va="top", fontsize=9.5, color=PAL["ink_secondary"])
    for _yr, _col in PAL["year"].items():
        _pts = day.loc[day["year"] == _yr]
        _ax.scatter(_pts["temp_c"], _pts["cnt"], s=10, color=_col, alpha=0.3, linewidths=0, zorder=1)
        _b = _bands.loc[_bands["year"] == _yr]
        _ax.plot(_b["t_mid"], _b["median"], color=_col, zorder=3, label=f"{_yr}: median per 3 °C band", linestyle="--" if _yr == 2011 else "-")
        _thin = _b["n"] < 10  # 5 to 9 days: shown, but hollow
        _ax.scatter(_b.loc[~_thin, "t_mid"], _b.loc[~_thin, "median"], s=50, color=_col,
                    edgecolor="white", linewidth=1.5, zorder=4)
        _ax.scatter(_b.loc[_thin, "t_mid"], _b.loc[_thin, "median"], s=50, facecolor="white",
                    edgecolor=_col, linewidth=1.5, zorder=4)
    _ax.set_xlabel("Daily mean temperature (°C)")
    _ax.set_ylabel("Rentals per day")
    _ax.yaxis.set_major_formatter(thousands)
    _ax.set_ylim(0, None)
    _ax.set_title(f"Daily rentals by temperature, {len(day):,} days")
    _ax.legend(loc="upper left")
    fig_temp.tight_layout(rect=(0, 0.16, 1, 1))
    # number of days per band and year, printed under the axis
    _counts = (day.assign(band=pd.cut(day["temp_c"], TEMP_EDGES, right=False))
               .groupby(["year", "band"], observed=True).size().unstack("year", fill_value=0))
    _position = _ax.get_position()
    _count_ax = fig_temp.add_axes([_position.x0, 0.055, _position.width, 0.065])
    _count_ax.set_xlim(_ax.get_xlim())
    _count_ax.set_ylim(-0.5, 1.5)
    _count_ax.axis("off")
    for _row, _yr in enumerate((2012, 2011)):
        _count_ax.text(-0.01, (_row + 0.5) / 2, f"{_yr} n", transform=_count_ax.transAxes,
                       ha="right", va="center", fontsize=8, color=PAL["ink_secondary"])
        for _band, _r in _counts.iterrows():
            _count_ax.text(_band.left + 1.5, _row, str(int(_r.get(_yr, 0))),
                           ha="center", va="center", fontsize=8, color=PAL["ink_secondary"])
    fig_temp.text(0.99, 0.01, "Numbers below the axis: days per band. Hollow markers: 5 to 9 days. Dots: single days.",
                  ha="right", va="bottom", fontsize=9, color=PAL["ink_secondary"])

    # numbers for the text; the reference is the busiest band with at least 10 days
    _means = day.groupby("year")["cnt"].mean()
    temp_facts = {"rho_all": bd.spearman(day["temp_c"], day["cnt"]), "growth": _means[2012] / _means[2011]}
    for _yr in (2011, 2012):
        _y = day.loc[day["year"] == _yr]
        _b = _bands.loc[(_bands["year"] == _yr) & (_bands["n"] >= 10)]
        _peak = _b.loc[_b["median"].idxmax()]
        _plateau = _b.loc[(_b["t_mid"] > 15) & (_b["t_mid"] < 30)]
        temp_facts[_yr] = {
            "rho": bd.spearman(_y["temp_c"], _y["cnt"]),
            "peak_band": f"{_peak['t_band'].left:.0f}-{_peak['t_band'].right:.0f} °C",
            "peak_median": _peak["median"],
            "plateau_min_ratio": _plateau["median"].min() / _peak["median"],
            "cold_ratio": _y.loc[_y["temp_c"] < 6, "cnt"].median() / _peak["median"],
            "n_cold": int((_y["temp_c"] < 6).sum()),
            "hot_ratio": _y.loc[_y["temp_c"] >= 30, "cnt"].median() / _peak["median"],
            "n_hot": int((_y["temp_c"] >= 30).sum()),
        }
    fig_temp
    return (temp_facts,)


@app.cell(hide_code=True)
def _(mo, temp_facts):
    _a, _b = temp_facts[2011], temp_facts[2012]
    mo.md(f"""
    Below 6 °C a typical day has only {_a['cold_ratio']:.0%} (2011) and {_b['cold_ratio']:.0%} (2012) of the rentals in the busiest band. Between 15 and 30 °C the medians stay within {1 - min(_a['plateau_min_ratio'], _b['plateau_min_ratio']):.0%} of that peak. The hottest band has just {_a['n_hot']} and {_b['n_hot']} days, so its dip is only a hint.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. Warmer than usual days have more rentals in winter and slightly fewer in summer
    """)
    return


@app.cell(hide_code=True)
def _(WINDOW_DAYS, mo):
    mo.md(f"""
    Finding 1 mostly shows the seasons. Is a day that is warm for its time of year also busier? We compare each day with the other days of the same year that are at most {WINDOW_DAYS} days away: rentals as a ratio to the median of the neighbours with the same day type, temperature as the difference to the neighbours' mean. Then we compute the Spearman rank correlation of the two, overall and per season. A moving window follows the season more closely than a calendar month, and leaving the day itself out means it is not compared with itself.
    """)
    return


@app.cell
def _(PAL, WINDOW_DAYS, bd, day, np, pd, plt):
    # compare each day with the other days of the same year that are at most WINDOW_DAYS away
    # rentals: median of the neighbours with the same day type (at least 3 of them)
    # weather: mean of all neighbours
    day_dev = day.sort_values("dteday").copy()
    _dates = day_dev["dteday"].to_numpy()
    _years = day_dev["year"].to_numpy()
    _day_types = day_dev["workingday"].to_numpy()
    _counts = day_dev["cnt"].to_numpy(dtype=float)
    _weather_columns = ("temp_c", "hum_pct", "wind_scaled")
    _weather = {_c: day_dev[_c].to_numpy(dtype=float) for _c in _weather_columns}
    _count_ref = np.full(len(day_dev), np.nan)
    _weather_ref = {_c: np.full(len(day_dev), np.nan) for _c in _weather_columns}
    for _i in range(len(day_dev)):
        _gap = np.abs((_dates - _dates[_i]) / np.timedelta64(1, "D"))
        _near = (_gap > 0) & (_gap <= WINDOW_DAYS) & (_years == _years[_i])
        _peers = _near & (_day_types == _day_types[_i])
        if _peers.sum() >= 3:
            _count_ref[_i] = np.median(_counts[_peers])
        for _c in _weather_columns:
            _weather_ref[_c][_i] = np.nanmean(_weather[_c][_near])
    day_dev["cnt_dev"] = _counts / _count_ref - 1
    for _c in _weather_columns:
        day_dev[f"{_c}_dev"] = _weather[_c] - _weather_ref[_c]
    _ok = day_dev.dropna(subset=["cnt_dev", "temp_c_dev"])
    _rows = [
        {"group": "All days, raw", "rho": bd.spearman(day["temp_c"], day["cnt"]),
         "n": len(day), "mean_temp": day["temp_c"].mean()},
        {"group": "All days, day to day", "rho": bd.spearman(_ok["temp_c_dev"], _ok["cnt_dev"]),
         "n": len(_ok), "mean_temp": _ok["temp_c"].mean()},
    ]
    for _season, _g in _ok.groupby("season_name", observed=True):
        _rows.append({"group": str(_season), "rho": bd.spearman(_g["temp_c_dev"], _g["cnt_dev"]),
                      "n": len(_g), "mean_temp": _g["temp_c"].mean()})
    rho_table = pd.DataFrame(_rows).set_index("group")

    # the same correlation with calendar months as baseline, for comparison in the text
    month_dev = day.copy()
    month_dev["cnt_dev"] = (day["cnt"] /
        day.groupby(["year", "mnth", "workingday"])["cnt"].transform("median") - 1)
    month_dev["temp_c_dev"] = day["temp_c"] - day.groupby(["year", "mnth"])["temp_c"].transform("mean")
    _month_ok = month_dev.dropna(subset=["temp_c_dev", "cnt_dev"])
    _month_rho = {"All days": bd.spearman(_month_ok["temp_c_dev"], _month_ok["cnt_dev"])}
    for _season, _g in _month_ok.groupby("season_name", observed=True):
        _month_rho[str(_season)] = bd.spearman(_g["temp_c_dev"], _g["cnt_dev"])
    rho_calendar_month = pd.Series(_month_rho)

    _labels = [
        f"All days, raw\n{int(rho_table.loc['All days, raw', 'n']):,} days",
        "All days,\nday to day",
    ] + [f"{s} (day to day)\n{int(r.n)} days, mean {r.mean_temp:.0f} °C" for s, r in rho_table.iloc[2:].iterrows()]
    _ypos = [0, 1, 2.6, 3.6, 4.6, 5.6]  # small gap between the overall bars and the seasons
    # winter and summer are highlighted because the slide title is about them
    _colors = [PAL["axis"], PAL["context"]] + [PAL["focus"] if s in ("Winter", "Summer") else PAL["context"]
                                               for s in rho_table.index[2:]]

    fig_season, _ax = plt.subplots(figsize=(10, 3.9))
    _ax.barh(_ypos, rho_table["rho"], height=0.42, color=_colors, zorder=2)
    _ax.spines["left"].set_visible(False)
    for _y, _r in zip(_ypos, rho_table["rho"]):
        _ax.text(_r + (0.015 if _r >= 0 else -0.015), _y, f"{_r:+.2f}",
                 va="center", ha="left" if _r >= 0 else "right", fontsize=10, color=PAL["ink"])
    _ax.axvline(0, color=PAL["ink_secondary"], lw=1, zorder=3)
    _ax.set_yticks(_ypos, _labels)
    _ax.invert_yaxis()
    _ax.set_xlim(-1, 1)
    _ax.grid(axis="y", visible=False)
    _ax.set_xlabel(f"Spearman correlation of the raw values, or of the deviations from the days within {WINDOW_DAYS} days")
    _ax.set_title("Temperature vs rentals, raw and day to day")
    fig_season.tight_layout()
    fig_season
    return day_dev, month_dev, rho_calendar_month, rho_table


@app.cell(hide_code=True)
def _(mo, rho_calendar_month, rho_table):
    _r = rho_table["rho"]
    mo.md(f"""
    Once the seasonal level is taken out, the link is weak overall ({_r['All days, day to day']:+.2f}, raw {_r['All days, raw']:+.2f}) and changes sign with the season: in winter a milder day has more rentals ({_r['Winter']:+.2f}), in summer a hotter day slightly fewer ({_r['Summer']:+.2f}). Calendar-month baselines give the same signs with larger values (summer {rho_calendar_month['Summer']:+.2f}).
    """)
    return


@app.cell
def _(BLOCK_DAYS, MATCH_KEYS, MIST, N_BOOT, RAIN, SEED, hour, np, pd):
    # 95% intervals for the mist and rain ratios (all, casual and registered rentals).
    # Neighbouring days are alike, so we resample whole weeks within each year and
    # recompute the clear-weather reference in every resample.
    _outcomes = ("cnt", "casual", "registered")
    _rng = np.random.default_rng(SEED)
    _days, _day_pos = np.unique(hour["dteday"].to_numpy(), return_inverse=True)
    _stamp = pd.DatetimeIndex(_days)
    # weeks start again on 1 January, so the last block of a year can be shorter
    _block = pd.factorize(_stamp.year * 1000 + (_stamp.dayofyear - 1) // BLOCK_DAYS)[0]
    _block_year = pd.Series(_stamp.year).groupby(_block).first().to_numpy()
    _years = np.unique(_block_year)
    _cell = hour.groupby(MATCH_KEYS).ngroup().to_numpy()
    _n_cell = _cell.max() + 1
    _code = hour["weather3_code"].to_numpy()
    _clear = _code == 1
    _values = {_kind: hour[_kind].to_numpy(dtype=float) for _kind in _outcomes}
    # the cells of the estimate (at least 3 clear hours) stay the same in every resample
    _in_estimate = np.bincount(_cell[_clear], minlength=_n_cell) >= 3

    _draws = []
    for _iteration in range(N_BOOT):
        _block_counts = np.zeros(_block.max() + 1)
        for _year in _years:
            _ids = np.flatnonzero(_block_year == _year)
            _block_counts += np.bincount(
                _ids[_rng.integers(0, len(_ids), len(_ids))], minlength=len(_block_counts))
        _day_weight = _block_counts[_block]
        _weight = _day_weight[_day_pos]
        _n = np.bincount(_cell[_clear], weights=_weight[_clear], minlength=_n_cell)
        _usable = (_in_estimate & (_n > 0))[_cell]  # a cell drops out only if none of its clear hours was drawn
        _row = []
        for _kind in _outcomes:
            _sum = np.bincount(_cell[_clear], weights=(_weight * _values[_kind])[_clear], minlength=_n_cell)
            with np.errstate(invalid="ignore", divide="ignore"):
                _expected = (_sum / _n)[_cell]
            for _weather_code in (2, 3):
                _mask = (_code == _weather_code) & _usable
                _row.append((_weight * _values[_kind])[_mask].sum() / (_weight * _expected)[_mask].sum())
        _rain = _code == 3
        _row.append(_weight[_rain & _usable].sum() / _weight[_rain].sum())
        _row.extend(_day_weight[_stamp.year == _year].sum() for _year in _years)
        _draws.append(_row)

    _draws = np.array(_draws)
    _n_ratio = 2 * len(_outcomes)
    _lo, _hi = np.percentile(_draws[:, :_n_ratio], [2.5, 97.5], axis=0)
    _index = pd.MultiIndex.from_product([list(_outcomes), [MIST, RAIN]], names=["y", "weather3"])
    weather_ci = pd.DataFrame({"lo": _lo, "hi": _hi}, index=_index)
    # quick checks of the resampling: share of rain hours kept and days per resampled year
    ci_info = {"rain_hours_kept": float(_draws[:, _n_ratio].mean()), "rain_mean": float(_draws[:, 1].mean())}
    for _j, _year in enumerate(_years):
        _d_lo, _d_hi = np.percentile(_draws[:, _n_ratio + 1 + _j], [2.5, 97.5])
        ci_info[f"days_{_year}"] = {"observed": int((_stamp.year == _year).sum()), "lo": float(_d_lo), "hi": float(_d_hi)}
    return ci_info, weather_ci


@app.cell(hide_code=True)
def _(RAIN, mo, weather_cmp):
    mo.md(f"""
    ## 3. Rain or snow hours have about {1 - weather_cmp.loc[RAIN, 'matched']:.0%} fewer rentals than comparable clear hours
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How much lower are rentals in mist and in rain or snow? Bad weather is not spread evenly over the calendar (see the EDA), so a plain comparison of averages would mix the weather with the time when it happens. We therefore compare each hour with clear hours of the same year, month, day type and hour of day (at least 3 of them) and divide the total observed rentals by the total expected rentals. The 95% interval comes from resampling whole weeks, because rainy days come in groups.
    """)
    return


@app.cell
def _(CLEAR, MATCH_KEYS, MIST, PAL, RAIN, hour, np, pd, plt, weather_ci):
    # for each rental type, attach the mean of the clear hours with the same timing
    # and keep the cells with at least 3 clear hours (also used in findings 4 and 5)
    matched_hours = {}
    for _kind in ("cnt", "casual", "registered"):
        _reference = (hour.loc[hour["weather3_code"] == 1]
            .groupby(MATCH_KEYS)[_kind]
            .agg(expected="mean", n_clear="size", clear_sum="sum"))
        _joined = hour.join(_reference, on=MATCH_KEYS, validate="many_to_one")
        matched_hours[_kind] = _joined.loc[_joined["n_clear"] >= 3].copy()

    # matched ratio = total observed / total expected (not a mean of hourly ratios)
    _groups = matched_hours["cnt"].groupby("weather3", observed=True)
    _means = hour.groupby("weather3", observed=True)["cnt"].mean()
    weather_cmp = pd.DataFrame({
        "n_hours": hour.groupby("weather3", observed=True).size(),
        "n_matched": _groups.size(),
        "naive": _means / _means[CLEAR],
        "matched": _groups["cnt"].sum() / _groups["expected"].sum().replace(0, np.nan),
    })

    _cats = [MIST, RAIN]
    fig_weather, _ax = plt.subplots(figsize=(10, 3.4))
    for _i, _cat in enumerate(_cats):
        _naive = (weather_cmp.loc[_cat, "naive"] - 1) * 100
        _ax.barh(_i - 0.17, _naive, height=0.3, color=PAL["context"], zorder=2,
                 label="Simple comparison of averages" if _i == 0 else None)
        _ax.text(_naive - 0.8, _i - 0.17, f"{_naive:+.0f}%", va="center", ha="right", fontsize=10, color=PAL["ink"])
        _v = (weather_cmp.loc[_cat, "matched"] - 1) * 100
        _lo, _hi = (weather_ci.loc[("cnt", _cat), ["lo", "hi"]].to_numpy() - 1) * 100
        _ax.barh(_i + 0.17, _v, height=0.3, color=PAL["focus"], zorder=2,
                 label="Matched: same hour, day type, month and year" if _i == 0 else None)
        _ax.errorbar(_v, _i + 0.17, xerr=[[_v - _lo], [_hi - _v]], fmt="none", ecolor=PAL["ink"],
                     elinewidth=1.2, capsize=4, zorder=4, label="95% interval (7-day blocks)" if _i == 0 else None)
        _ax.text(_lo - 0.8, _i + 0.17, f"{_v:+.0f}%", va="center", ha="right", fontsize=10, color=PAL["ink"])
    _ax.axvline(0, color=PAL["ink_secondary"], lw=1, zorder=3)
    _ax.set_yticks(range(len(_cats)), [f"{c}\n{int(weather_cmp.loc[c, 'n_hours']):,} raw / {int(weather_cmp.loc[c, 'n_matched']):,} matched" for c in _cats])
    _ax.invert_yaxis()
    _ax.set_xlim(-62, 4)
    _ax.grid(axis="y", visible=False)
    _ax.spines["left"].set_visible(False)
    _ax.set_xlabel("Difference from clear-weather reference (%)")
    _ax.set_title(f"Observed vs expected rentals, {len(hour):,} hours "
                  f"({weather_cmp.loc[CLEAR, 'n_hours']:,} clear)")
    _ax.legend(loc="upper left")
    fig_weather.tight_layout()
    fig_weather
    return matched_hours, weather_cmp


@app.cell(hide_code=True)
def _(MIST, RAIN, mo, weather_ci, weather_cmp):
    _m, _r = weather_cmp.loc[MIST], weather_cmp.loc[RAIN]
    _ci_m, _ci_r = weather_ci.loc[("cnt", MIST)], weather_ci.loc[("cnt", RAIN)]
    mo.md(f"""
    Rain/snow hours have {1 - _r['matched']:.0%} fewer rentals (95% interval {(1 - _ci_r['hi']) * 100:.0f}-{(1 - _ci_r['lo']) * 100:.0f}%), misty hours {1 - _m['matched']:.0%} fewer ({(1 - _ci_m['hi']) * 100:.0f}-{(1 - _ci_m['lo']) * 100:.0f}%). A plain comparison of averages gives {_m['naive'] - 1:+.0%} for mist, because misty hours fall more often at quiet times; for rain both methods agree ({_r['naive'] - 1:+.0%}). Temperature and the other weather variables are not held fixed.
    """)
    return


@app.cell(hide_code=True)
def _(mo, wind_table):
    mo.md(f"""
    ## 4. In clear weather, humid hours look almost normal, but the windiest hours have {1 - wind_table['ratio_clear'].iloc[-1]:.0%} fewer rentals
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Do humidity and wind go with fewer rentals on their own, or mostly because they come with rain? We use the same observed vs expected ratio per humidity and wind band, once for all hours and once for clear hours only. Very humid hours are often rainy, so the clear-only curve takes the rain out without needing a model. In the clear-only curve each hour is left out of its own reference. Wind is grouped on the original scale (67 x windspeed, rounded) because its unit is not documented.
    """)
    return


@app.cell
def _(
    HUM_EDGES,
    HUM_LABELS,
    PAL,
    WIND_EDGES,
    WIND_LABELS,
    matched_hours,
    pd,
    plt,
):
    # humidity and wind bands, using the same matched hours as finding 3
    _base = matched_hours["cnt"].assign(
        hum_band=pd.cut(matched_hours["cnt"]["hum_pct"], HUM_EDGES, right=False, labels=HUM_LABELS),
        wind_band=pd.cut(matched_hours["cnt"]["wind_rounded"], WIND_EDGES, labels=WIND_LABELS),
    )
    _clear = _base.loc[_base["weather3_code"] == 1].copy()
    # each clear hour is left out of its own reference (at least 2 others remain)
    _clear["expected_loo"] = (_clear["clear_sum"] - _clear["cnt"]) / (_clear["n_clear"] - 1)
    _band_tables = {}
    for _band in ("hum_band", "wind_band"):
        _all_hours = _base.groupby(_band, observed=True)
        _clear_hours = _clear.groupby(_band, observed=True)
        _band_tables[_band] = pd.DataFrame({
            "n_all": _all_hours.size(),
            "ratio_all": _all_hours["cnt"].sum() / _all_hours["expected"].sum(),
            "n_clear": _clear_hours.size(),
            "ratio_clear": _clear_hours["cnt"].sum() / _clear_hours["expected_loo"].sum(),
            "ratio_clear_inclusive": _clear_hours["cnt"].sum() / _clear_hours["expected"].sum(),  # without leaving out
            "rain_share": _base["weather3_code"].eq(3).groupby(_base[_band], observed=True).mean(),
        })
    hum_table, wind_table = _band_tables["hum_band"], _band_tables["wind_band"]

    fig_humwind, _axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for _ax, _tab, _xlabel in [(_axes[0], hum_table, "Relative humidity (%)"),
                               (_axes[1], wind_table, "Rounded wind (67 x windspeed)\nphysical unit unknown")]:
        _x = range(len(_tab))
        _ax.axhline(0, color=PAL["ink_secondary"], lw=1, zorder=2)
        _ax.plot(_x, (_tab["ratio_all"] - 1) * 100, color=PAL["context"], marker="o", ms=7,
                 mec="white", mew=1.5, zorder=3, label="All hours")
        _ax.plot(_x, (_tab["ratio_clear"] - 1) * 100, color=PAL["focus"], marker="o", ms=7,
                 mec="white", mew=1.5, zorder=4, label="Clear hours (hour left out of its reference)")
        for _col, _dy in [("ratio_all", -1), ("ratio_clear", 1)]:
            _last = (_tab[_col].iloc[-1] - 1) * 100
            _ax.annotate(f"{_last:+.0f}%", (len(_tab) - 1, _last), xytext=(8, 4 * _dy),
                         textcoords="offset points", va="center", fontsize=10, color=PAL["ink"])
        _ax.set_xticks(list(_x), [f"{b}\n{int(r.n_all):,} / {int(r.n_clear):,}" for b, r in _tab.iterrows()])
        _ax.set_xlim(-0.4, len(_tab) - 0.15)
        _ax.tick_params(axis="x", labelsize=8.5)
        _ax.set_xlabel(_xlabel)
        _ax.grid(axis="x", visible=False)
    _axes[0].set_ylabel("Rentals vs clear-weather\nexpectation (%)")
    _axes[0].legend(loc="lower left")
    fig_humwind.suptitle("Observed / expected rentals by band (numbers under the bands: all / clear hours)",
                         x=0.01, ha="left", fontsize=11.5, fontweight="bold", color=PAL["ink"])
    fig_humwind.tight_layout()
    fig_humwind
    return hum_table, wind_table


@app.cell(hide_code=True)
def _(cutoff_check, hum_table, mo, wind_table):
    _h, _w = hum_table.iloc[-1], wind_table.iloc[-1]
    _gap = 1 - cutoff_check.set_index("top band")["observed / expected"]
    mo.md(f"""
    Over all hours, very humid hours (85% and more) have {1 - _h['ratio_all']:.0%} fewer rentals, but {_h['rain_share']:.0%} of them are rainy. In clear weather the gap shrinks to {1 - _h['ratio_clear']:.0%}. The windiest hours keep a gap even when clear ({1 - _w['ratio_clear']:.0%}, {1 - _w['ratio_all']:.0%} over all hours); with the cut at 25 or 35 instead of 30 it is {_gap['wind above 25']:.0%} or {_gap['wind above 35']:.0%}. Humidity, wind and rain overlap, so these gaps are not separate effects.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Casual rentals drop more than registered rentals in cold and rain
    """)
    return


@app.cell(hide_code=True)
def _(day, mo):
    _share = day.groupby("workingday")[["casual", "cnt"]].sum()
    _share = _share["casual"] / _share["cnt"]
    mo.md(f"""
    Do casual and registered users react to cold and rain in the same way? Casual users make {_share[0]:.0%} of the rentals on non-working days but {_share[1]:.0%} on working days, so raw counts would mix user type with day type. We therefore compare each group with its own typical day: (a) daily counts as a share of the group's median on 21 to 24 °C days of the same year and day type, (b) the mist and rain ratios from finding 3 for each group, with 95% intervals.
    """)
    return


@app.cell
def _(
    MIST,
    PAL,
    RAIN,
    TEMP_EDGES,
    day,
    matched_hours,
    np,
    pd,
    plt,
    weather_ci,
    weather_cmp,
):
    # reference for each user type: its median on 21-24 °C days of the same year and day type
    _user_days = day.copy()
    _reference = (day.loc[(day["temp_c"] >= 21) & (day["temp_c"] < 24)]
        .groupby(["year", "workingday"])[["casual", "registered"]].median())
    _user_days = _user_days.join(_reference.add_suffix("_reference"),
        on=["year", "workingday"], validate="many_to_one")
    for _kind in ("casual", "registered"):
        _user_days[f"{_kind}_idx"] = _user_days[_kind] / _user_days[f"{_kind}_reference"]
    _user_days["t_band"] = pd.cut(_user_days["temp_c"], TEMP_EDGES, right=False)
    user_temp = (_user_days.groupby("t_band", observed=True)
        .agg(casual=("casual_idx", "median"), registered=("registered_idx", "median"), n=("cnt", "size")))
    user_temp = user_temp.loc[user_temp["n"] >= 5]
    user_temp["t_mid"] = [_band.left + 1.5 for _band in user_temp.index]
    _cold, _hot = _user_days.loc[_user_days["temp_c"] < 6], _user_days.loc[_user_days["temp_c"] >= 30]
    user_cold = {"casual": _cold["casual_idx"].median(), "registered": _cold["registered_idx"].median(), "n_days": len(_cold)}
    user_hot = {"casual": _hot["casual_idx"].median(), "registered": _hot["registered_idx"].median(), "n_days": len(_hot)}

    # hourly mist and rain ratios, each user type with its own clear-weather reference
    _user_ratios = {}
    for _kind in ("casual", "registered"):
        _groups = matched_hours[_kind].groupby("weather3", observed=True)
        _user_ratios[_kind] = _groups[_kind].sum() / _groups["expected"].sum().replace(0, np.nan)
    user_weather = pd.DataFrame(_user_ratios)

    fig_users, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 3.8), width_ratios=[1.45, 1])
    _ax1.axhline(100, color=PAL["ink_secondary"], lw=1, zorder=2)
    for _t in ("casual", "registered"):
        _ax1.plot(user_temp["t_mid"], user_temp[_t] * 100, color=PAL["user"][_t], marker="o", ms=7,
                  mec="white", mew=1.5, zorder=3, label=_t.capitalize())
    _ax1.text(user_temp["t_mid"].min(), 102, "Same year and day type reference = 100%", va="bottom",
              fontsize=9, color=PAL["ink_secondary"])
    _ax1.set_ylim(0, max(120, float(user_temp[["casual", "registered"]].max().max()) * 110))
    _ax1.set_xlabel("Daily mean temperature (°C); days per 3 °C band below")
    _ax1.set_ylabel("% of the type's 21-24 °C median\n(same year and day type)")
    _ax1.set_title(f"(a) Rentals by temperature, per user type, {int(user_temp['n'].sum())} days")
    _ax1.legend(loc="lower right")
    _ax1.set_xticks(user_temp["t_mid"], [f"{x:g}\n{int(n)}" for x, n in zip(user_temp["t_mid"], user_temp["n"])],
                    fontsize=8)

    _cats = [MIST, RAIN]
    for _i, _cat in enumerate(_cats):
        for _shift, _t in [(-0.17, "casual"), (0.17, "registered")]:
            _v = (user_weather.loc[_cat, _t] - 1) * 100
            _lo, _hi = (weather_ci.loc[(_t, _cat), ["lo", "hi"]].to_numpy() - 1) * 100
            _ax2.barh(_i + _shift, _v, height=0.26, color=PAL["user"][_t], zorder=2,
                      label=_t.capitalize() if _i == 0 else None)
            _ax2.errorbar(_v, _i + _shift, xerr=[[_v - _lo], [_hi - _v]], fmt="none", ecolor=PAL["ink"],
                          elinewidth=1.2, capsize=3, zorder=4)
            _ax2.text(_lo - 1, _i + _shift, f"{_v:+.0f}%", va="center", ha="right", fontsize=10, color=PAL["ink"])
    _ax2.axvline(0, color=PAL["ink_secondary"], lw=1, zorder=3)
    _matched_counts = weather_cmp["n_matched"]
    _ax2.set_yticks(range(len(_cats)), [f"{c}\n{int(_matched_counts.loc[c]):,} matched h" for c in _cats])
    _ax2.invert_yaxis()
    _ax2.set_xlim(-85, 3)
    _ax2.grid(axis="y", visible=False)
    _ax2.spines["left"].set_visible(False)
    _ax2.legend(loc="upper left")
    _ax2.set_xlabel("Difference from clear reference (%), 95% intervals")
    _ax2.set_title("(b) Mist and rain, per user type")
    fig_users.tight_layout()
    fig_users
    return user_cold, user_hot, user_temp, user_weather


@app.cell(hide_code=True)
def _(RAIN, mo, user_cold, user_hot, user_weather, weather_ci):
    _c, _r = weather_ci.loc[("casual", RAIN)], weather_ci.loc[("registered", RAIN)]
    mo.md(f"""
    On cold days (below 6 °C) casual rentals reach only {user_cold['casual']:.0%} of their usual level, registered rentals {user_cold['registered']:.0%}. In rain/snow casual rentals fall {1 - user_weather.loc[RAIN, 'casual']:.0%} (95% interval {(1 - _c['hi']) * 100:.0f}-{(1 - _c['lo']) * 100:.0f}%), registered {1 - user_weather.loc[RAIN, 'registered']:.0%} ({(1 - _r['hi']) * 100:.0f}-{(1 - _r['lo']) * 100:.0f}%). On the {user_hot['n_days']} hot days (30 °C and more) casual and registered rentals are {1 - user_hot['casual']:.0%} and {1 - user_hot['registered']:.0%} below their usual level, too few days to tell the groups apart.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Temperature tracks the seasonal level, the weather category tracks day-to-day swings
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Which goes more with rentals, temperature or the weather category, and does it depend on the time scale? We use eta squared, the share of the variation in daily rentals that lies between groups: once on the raw daily counts (across the year) and once on the day-to-day deviations from finding 2. Temperature is cut into three equal groups, so both variables have three groups. The values still depend on where the cuts fall, so we compare sizes rather than exact numbers.
    """)
    return


@app.cell
def _(PAL, TEMP_EDGES, WINDOW_DAYS, bd, day, day_dev, pd, plt):
    # eta squared for temperature (three equal groups) and the three weather categories
    _ok = day_dev.dropna(subset=["cnt_dev", "temp_c_dev"])
    _samples = [("Across the year", day, "cnt", "temp_c"),
                ("Day to day, all seasons", _ok, "cnt_dev", "temp_c_dev")]
    for _season, _g in _ok.groupby("season_name", observed=True):
        _samples.append((f"Day to day, {str(_season).lower()}", _g, "cnt_dev", "temp_c_dev"))
    _rows, _n = {}, []
    for _label, _sample, _response, _temperature in _samples:
        _rows[_label] = {
            "Temperature (thirds)": bd.eta_squared(_sample[_response], pd.qcut(_sample[_temperature], 3, labels=False)),
            "Weather category": bd.eta_squared(_sample[_response], _sample["weather3"]),
        }
        _n.append(len(_sample))
    eta_table = pd.DataFrame(_rows).T
    eta_table["n_days"] = _n
    eta_temp_13_bands = bd.eta_squared(day["cnt"], pd.cut(day["temp_c"], TEMP_EDGES, right=False))  # 13 bands, for comparison
    weather_days = day["weather3"].value_counts().sort_index()

    _ypos = [0, 1.4, 2.4, 3.4, 4.4, 5.4]  # small gap between "across the year" and "day to day"
    fig_eta, _ax = plt.subplots(figsize=(10.5, 4.2))
    for _shift, _col, _color in [(-0.18, "Temperature (thirds)", PAL["user"]["casual"]),
                                 (0.18, "Weather category", PAL["focus"])]:
        _ax.barh([y + _shift for y in _ypos], eta_table[_col], height=0.34, color=_color, label=_col, zorder=2)
        for _y, _v in zip(_ypos, eta_table[_col]):
            _ax.text(_v + 0.005, _y + _shift, f"{_v:.2f}", va="center", ha="left", fontsize=9.5, color=PAL["ink"])
    _ax.set_yticks(_ypos, [f"{name}\n{int(n)} days" for name, n in zip(eta_table.index, eta_table["n_days"])])
    _ax.invert_yaxis()
    _ax.set_xlim(0, 0.5)
    _ax.grid(axis="y", visible=False)
    _ax.spines["left"].set_visible(False)
    _ax.set_xlabel("Eta squared: share of the variation in daily rentals between the three groups")
    _ax.set_title("Temperature vs weather category, each in three groups")
    _ax.legend(loc="lower right")
    fig_eta.tight_layout(rect=(0, 0.05, 1, 1))
    fig_eta.text(0.99, 0.01,
                 f"Day to day: deviations from the other days of the same year within {WINDOW_DAYS} days. "
                 f"Weather days: {weather_days.iloc[0]} clear, {weather_days.iloc[1]} mist, {weather_days.iloc[2]} rain/snow.",
                 ha="right", va="bottom", fontsize=9, color=PAL["ink_secondary"])
    fig_eta
    return eta_table, eta_temp_13_bands, weather_days


@app.cell(hide_code=True)
def _(eta_table, eta_temp_13_bands, mo):
    _t = eta_table["Temperature (thirds)"]
    _w = eta_table["Weather category"]
    mo.md(f"""
    Across the year, temperature groups separate daily rentals far more than weather categories ({_t['Across the year']:.2f} vs {_w['Across the year']:.2f}; {eta_temp_13_bands:.2f} with 13 temperature bands). Day to day the order reverses ({_t['Day to day, all seasons']:.2f} vs {_w['Day to day, all seasons']:.2f}); in winter the two are of similar size under this grouping ({_t['Day to day, winter']:.2f} vs {_w['Day to day, winter']:.2f}). Eta squared shows how rentals split by group; it does not divide them into separate parts for temperature, season and rain.
    """)
    return


@app.cell(hide_code=True)
def _(
    MIST,
    RAIN,
    cutoff_check,
    eta_table,
    mo,
    rho_table,
    temp_facts,
    user_cold,
    user_weather,
    weather_ci,
    weather_cmp,
    wind_table,
):
    _rain = weather_cmp.loc[RAIN, "matched"]
    _ci = weather_ci.loc[("cnt", RAIN)]
    _t, _w = eta_table["Temperature (thirds)"], eta_table["Weather category"]
    _cold = sorted([temp_facts[2011]["cold_ratio"], temp_facts[2012]["cold_ratio"]])
    _wind_cuts = cutoff_check.loc[cutoff_check["top band"].str.startswith("wind"), "observed / expected"]
    mo.md(f"""
    ## Conclusion

    Answer to Q4: rental activity is higher in warmer parts of the year, while rain/snow hours have about {1 - _rain:.0%} fewer rentals than comparable clear hours.

    1. Across the year, rentals rise with temperature up to about 15 °C. Below 6 °C a typical day has {_cold[0] * 100:.0f}-{_cold[1]:.0%} of the rentals of the busiest band; between 15 and 30 °C the level stays roughly flat.
    2. Day to day, the pattern depends on the season. A warmer than usual day has more rentals in winter ({rho_table.loc['Winter', 'rho']:+.2f}) and slightly fewer in summer ({rho_table.loc['Summer', 'rho']:+.2f}).
    3. Rain shows the largest gap: rain/snow hours have {1 - _rain:.0%} fewer rentals (95% interval {(1 - _ci['hi']) * 100:.0f}-{(1 - _ci['lo']) * 100:.0f}%), misty hours {1 - weather_cmp.loc[MIST, 'matched']:.0%} fewer. In clear weather humidity shows little gap, while the windiest hours still have {1 - wind_table['ratio_clear'].iloc[-1]:.0%} fewer ({(1 - _wind_cuts.max()) * 100:.0f}-{1 - _wind_cuts.min():.0%} depending on the cut-off).
    4. Casual rentals drop more. In cold they reach {user_cold['casual']:.0%} of their usual level (registered {user_cold['registered']:.0%}), in rain they fall {1 - user_weather.loc[RAIN, 'casual']:.0%} (registered {1 - user_weather.loc[RAIN, 'registered']:.0%}).
    5. The time scale matters. Temperature tracks the seasonal level (eta squared {_t['Across the year']:.2f} vs {_w['Across the year']:.2f}), the weather category tracks day-to-day swings ({_w['Day to day, all seasons']:.2f} vs {_t['Day to day, all seasons']:.2f}).
    """)
    return


@app.cell(hide_code=True)
def _(
    MATCH_KEYS,
    RAIN,
    WINDOW_DAYS,
    day,
    hour_all,
    mo,
    user_hot,
    weather_cmp,
    weather_days,
):
    # rain/snow ratio when the poorly covered days are kept as well
    _reference = (hour_all.loc[hour_all["weather3_code"] == 1]
        .groupby(MATCH_KEYS)["cnt"].agg(expected="mean", n_clear="size"))
    _all_hours = hour_all.join(_reference, on=MATCH_KEYS, validate="many_to_one")
    _rain = _all_hours.loc[(_all_hours["n_clear"] >= 3) & (_all_hours["weather3"] == RAIN)]
    rain_all_dates = _rain["cnt"].sum() / _rain["expected"].sum()
    mo.md(f"""
    ## Limitations

    - Associations, not causes. Weather variables move together (rain with humidity and wind, temperature with season), and no comparison here isolates one of them.
    - Two years, one city: {len(day)} days in Washington D.C. with few extreme days, {user_hot['n_days']} days at 30 °C or more and {weather_days.loc[RAIN]} rain/snow days.
    - Gaps in the record. Poorly covered days are dropped and some night hours are missing; with all recorded days the rain/snow difference is {rain_all_dates - 1:+.0%} instead of {weather_cmp.loc[RAIN, 'matched'] - 1:+.0%}.
    - Coarse weather data. Categories hide intensity, the wind unit is unknown, and daily weather is an average of the recorded hours only.
    - Our own choices. The {WINDOW_DAYS}-day window, the 3 °C bands and the rule of at least 3 clear hours are choices; the checks in the EDA show that the conclusions hold under alternatives. The 95% intervals only cover resampling variability.
    """)
    return (rain_all_dates,)


if __name__ == "__main__":
    app.run()
