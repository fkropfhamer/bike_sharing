import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np

    return pd, plt


@app.cell
def _(pd):
    data_day = pd.read_csv("day.csv")
    data_hour = pd.read_csv("hour.csv")
    return data_day, data_hour


@app.cell
def _(data_day, data_hour):
    year_data = (
        data_day
        .groupby("yr")[["casual", "registered"]]
        .agg(["mean", "median", "count", "sum"])
        .reset_index()
    )

    month_data = (
        data_day
        .groupby("mnth")[["casual", "registered"]]
        .agg(["mean", "median", "count", "sum"])
        .reset_index()
    )

    weekday_data = (
        data_day
        .groupby("weekday")[["casual", "registered"]]
        .agg(["mean", "median", "count", "sum"])
        .reset_index()
    )

    hour_data = (
        data_hour
        .groupby("hr")[["casual", "registered"]]
        .agg(["mean", "median", "count", "sum"])
        .reset_index()
    )

    weathersit_data = (
        data_hour
        .groupby("weathersit")[["casual", "registered"]]
        .agg(["mean", "median", "count", "sum"])
        .reset_index()
    )
    return hour_data, month_data, weathersit_data, weekday_data, year_data


@app.cell
def _():
    casual_color = "#1a80bb"
    registered_color = "#ea801c"
    return casual_color, registered_color


@app.cell
def _(casual_color, month_data, plt, registered_color):
    month_user_means = {
        "registered": month_data[('registered', 'mean')],
        "casual": month_data[('casual', 'mean')]
    }


    _fig, _ax = plt.subplots()

    _res = _ax.grouped_bar(month_user_means, tick_labels=range(0,12), group_spacing=1, colors=[registered_color, casual_color])
    for _container in _res.bar_containers:
        _ax.bar_label(_container, padding=3)

    _ax.set_ylabel('Mean')
    _ax.set_title('Mean monthly usage by user group')
    _ax.legend(loc='upper left', ncols=3)

    plt.show()
    return


@app.cell
def _(casual_color, plt, registered_color, weekday_data):
    user_means = {
        "registered": weekday_data[('registered', 'mean')],
        "casual": weekday_data[('casual', 'mean')]
    }


    _fig, _ax = plt.subplots()

    _res = _ax.grouped_bar(user_means, tick_labels=range(0,7), group_spacing=1, colors=[registered_color, casual_color])
    for _container in _res.bar_containers:
        _ax.bar_label(_container, padding=3)

    _ax.set_ylabel('Mean')
    _ax.set_title('Mean weekday usage by user group')
    _ax.legend(loc='upper left', ncols=3)

    plt.show()
    return


@app.cell
def _(casual_color, hour_data, plt, registered_color):
    hour_user_means = {
        "registered": hour_data[('registered', 'mean')],
        "casual": hour_data[('casual', 'mean')]
    }


    _fig, _ax = plt.subplots()

    _res = _ax.grouped_bar(hour_user_means, tick_labels=range(0,24), group_spacing=1, colors=[registered_color, casual_color])
    for _container in _res.bar_containers:
        _ax.bar_label(_container, padding=3)

    _ax.set_ylabel('Mean')
    _ax.set_title('Mean hourly usage by user group')
    _ax.legend(loc='upper left', ncols=3)

    plt.show()
    return


@app.cell
def _(casual_color, plt, registered_color, weathersit_data):
    weathersit_user_means = {
        "registered": weathersit_data[('registered', 'mean')],
        "casual": weathersit_data[('casual', 'mean')]
    }


    _fig, _ax = plt.subplots()

    _res = _ax.grouped_bar(weathersit_user_means, tick_labels=weathersit_data['weathersit'].unique(), group_spacing=1, colors=[registered_color, casual_color])
    for _container in _res.bar_containers:
        _ax.bar_label(_container, padding=3)

    _ax.set_ylabel('Mean')
    _ax.set_title('Mean weahtercondition usage by user group')
    _ax.legend(loc='upper left', ncols=3)

    plt.show()
    return


@app.cell
def _(casual_color, plt, registered_color, year_data):
    groups = ["2011", "2012"]
    registerd_counts = year_data[('registered', 'sum')].sort_index()
    casual_counts = year_data[('casual', 'sum')].sort_index()

    totals = registerd_counts + casual_counts
    registered_pct = registerd_counts / totals * 100
    casual_pct = casual_counts / totals * 100

    _fig, _ax = plt.subplots()
    _b1 = _ax.bar(groups, casual_pct, label="casual", color=casual_color)
    _b2 = _ax.bar(groups, registered_pct, bottom=casual_pct, label="registered", color=registered_color)

    _ax.bar_label(_b1, fmt="%.1f%%", label_type="center", color="white")
    _ax.bar_label(_b2, fmt="%.1f%%", label_type="center", color="white")

    _ax.set_ylabel("Percentage (%)")
    _ax.set_ylim(0, 100)
    _ax.set_title("Group percentage per year")
    _ax.legend()

    plt.show()
    return


@app.cell
def _(casual_color, data_day, plt, registered_color):
    _fig, _ax = plt.subplots()

    _scale = 10
    _alpha = 0.6

    _ax.scatter(data_day["atemp"], data_day["registered"], c=registered_color, s=_scale, label="registered",
                   alpha=_alpha, edgecolors='none')
    _ax.scatter(data_day["atemp"], data_day["casual"], c=casual_color, s=_scale, label="casual",
                   alpha=_alpha, edgecolors='none')
    _ax.legend()
    _ax.grid(True)
    _ax.set_ylabel("Count")
    _ax.set_xlabel("Temperature")
    _ax.set_title("Rentals vs. Temparture by group")
    plt.show()
    return


if __name__ == "__main__":
    app.run()
