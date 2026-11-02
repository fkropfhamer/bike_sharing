import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", layout_file="layouts/question_1.slides.json")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    #**How does bike-sharing activity vary across weekdays, months, years and throughout the day?**
    ---
    """)
    return


@app.cell
def _():
    # Import some libraries
    # ---------------------
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator
    import pandas as pd

    return pd, plt


@app.cell
def _(pd):
    # Read data
    # ---------

    data_day = pd.read_csv("day.csv")
    data_hr = pd.read_csv("hour.csv")

    weekday_data = data_day.groupby(data_day["weekday"])["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    mnth_data = data_day.groupby("mnth")["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    mnth_data_2011 = data_day[data_day["yr"]==0].groupby("mnth")["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    mnth_data_2012 = data_day[data_day["yr"]==1].groupby("mnth")["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    yr_data = data_day.groupby("yr")["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    hr_data = data_hr.groupby("hr")["cnt"].agg(mean="mean", median="median", n="count").reset_index()

    #print(data_hr[data_hr["registered"] == 0][data_hr["casual"]==0])
    return data_day, hr_data, mnth_data, mnth_data_2011, mnth_data_2012


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Rental counts in weekdays**
    """)
    return


@app.cell
def _(data_day, mo, plt):
    fig_weekday, ax_weekday = plt.subplots(figsize=(12,9))
    ax_weekday.spines[['right', 'top']].set_visible(False)
    plt.boxplot([data_day[data_day["weekday"] == _]["cnt"] for _ in range(7)],
                tick_labels = ["Sun","Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], #0-6 corresponds to Sunday to Saturday
                patch_artist = True,
                showmeans = True,
                meanprops = {
                    "marker": "D",
                    "markerfacecolor": "#d95f02",
                    "markeredgecolor": "white",
                    "markersize": 7,
                },
                medianprops = {"color": "#1f2937", "linewidth": 2},
                boxprops = {"facecolor": "#dbeafe", "edgecolor": "#4b78a8"},
                whiskerprops = {"color": "#64748b"},
                capprops = {"color": "#64748b"},
                flierprops={
                    "marker": "o",
                    "markerfacecolor": "#94a3b8",
                    "markeredgecolor": "none",
                    "markersize": 4,
                    "alpha": 0.6,
                }
               )

    plt.xlabel("Weekdays", fontsize = 20, labelpad = 20)
    plt.ylabel("Daily rental counts", fontsize = 20, labelpad = 20)
    plt.title("Daily rental counts in weekdays", fontsize=30, pad = 20)
    ax_weekday.tick_params(axis="both", labelsize=20)
    ax_weekday.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_weekday.grid(color='gray', linestyle='--', linewidth=0.5)

    mo.center(fig_weekday)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##*Comment*:
    The mean daily rent amounts in two years 2011 and 2012 do not showcase big variation among the weekdays. Friday and Saturday are slightly busier days.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Rental counts in months**
    """)
    return


@app.cell
def _(mnth_data_2011, mnth_data_2012, mo, plt):
    fig_mnth, ax_mnth = plt.subplots(figsize=(18, 9))
    ax_mnth.spines[['right', 'top']].set_visible(False)
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    plt.plot(month_name, mnth_data_2011["mean"], linestyle = "--", marker = "o", label = "Year 2011")
    plt.plot(month_name, mnth_data_2012["mean"], linestyle = "--", marker = "o", color = "#d95f02", label = "Year 2012")
    plt.xlabel("Months", fontsize = 20, labelpad = 20)
    plt.ylabel("Mean daily rental counts", fontsize = 20, labelpad = 20)
    plt.title("Mean daily rental counts among months in years 2011 and 2012", fontsize = 30, pad = 20)
    ax_mnth.tick_params(axis="both", labelsize=20)
    ax_mnth.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_mnth.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.legend(fontsize = 20)
    mo.center(fig_mnth)
    return (month_name,)


@app.cell
def _():
    """
    fig_mnth_2012, ax_mnth_2012 = plt.subplots(figsize=(8,6))
    ax_mnth_2012.spines[['right', 'top']].set_visible(False)
    plt.bar(mnth_data_2012["mnth"], mnth_data_2012["mean"])
    plt.xlabel("Months")
    plt.ylabel("Mean daily rental counts")
    plt.title("Mean daily rental counts in months in 2012", fontsize = 15)
    ax_mnth_2012.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_mnth_2012.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
    """
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ***Highlight months with high mean daily rental counts (over 5000)***
    """)
    return


@app.cell
def _(mnth_data, mo, month_name, plt):
    highlight_colour_mnth = '#d95f02'
    non_highlight_colour_mnth = '#768493'
    cut_off_mnth = 5000
    mnth_data_copy = mnth_data.copy()
    mnth_data_copy["colours"] = mnth_data_copy["mean"].apply(lambda x: highlight_colour_mnth if x >= cut_off_mnth else non_highlight_colour_mnth)

    fig_mnth_2, ax_mnth_2 = plt.subplots(figsize=(18,9))
    ax_mnth_2.spines[['right', 'top']].set_visible(False)

    plt.bar(month_name, mnth_data_copy["mean"], color = mnth_data_copy["colours"])
    plt.xlabel("Months", fontsize = 20, labelpad = 20)
    plt.ylabel("Mean daily rental counts", fontsize = 20, labelpad = 20)
    plt.title("Mean daily rental counts in months", fontsize = 30, pad = 20)
    ax_mnth_2.tick_params(axis="both", labelsize=20)
    ax_mnth_2.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_mnth_2.grid(color='gray', linestyle='--', linewidth=0.5)
    mo.center(fig_mnth_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##*Comment*:
    The mean daily rent amounts in two years 2011 and 2012 for the months May to October all exceed 5000. This indicates a possible correlation between rental counts and weather.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Rental counts in years**
    """)
    return


@app.cell
def _(data_day, mo, plt):
    fig_yr, ax_yr = plt.subplots(figsize=(12,9))
    ax_yr.spines[['right', 'top']].set_visible(False)
    plt.boxplot([data_day[data_day["yr"] == _]["cnt"] for _ in range(2)],
                tick_labels = ["2011", "2012"],
                patch_artist = True,
                showmeans = True,
                meanprops = {
                    "marker": "D",
                    "markerfacecolor": "#d95f02",
                    "markeredgecolor": "white",
                    "markersize": 7,
                },
                medianprops = {"color": "#1f2937", "linewidth": 2},
                boxprops = {"facecolor": "#dbeafe", "edgecolor": "#4b78a8"},
                whiskerprops = {"color": "#64748b"},
                capprops = {"color": "#64748b"},
                flierprops={
                    "marker": "o",
                    "markerfacecolor": "#94a3b8",
                    "markeredgecolor": "none",
                    "markersize": 4,
                    "alpha": 0.6,
                }
               )
    plt.xlabel("Years", fontsize = 20, labelpad = 20)
    plt.ylabel("Daily rental counts", fontsize = 20, labelpad = 20)
    plt.title("Daily rental counts in years", fontsize = 30, pad = 20)
    ax_yr.tick_params(axis="both", labelsize=20)
    ax_yr.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_yr.grid(color='gray', linestyle='--', linewidth=0.5)
    mo.center(fig_yr)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##*Comment*:
    The mean daily rent amounts in 2012 clearly exceed that of year 2011. This indicates that Bike-Sharing was gaining more popularity.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Rental counts throughout the day**
    """)
    return


@app.cell
def _(hr_data, mo, plt):
    fig_hr, ax_hr = plt.subplots(figsize=(18,9))
    ax_hr.spines[['right', 'top']].set_visible(False)

    plt.plot(hr_data["hr"], hr_data["mean"], linestyle = "--", marker = "o")
    plt.xlabel("Hours", fontsize = 20, labelpad = 20)
    plt.ylabel("Mean hourly rental counts", fontsize = 20, labelpad = 20)
    plt.title("Mean hourly rental counts", fontsize = 30, pad = 20)
    ax_hr.tick_params(axis="both", labelsize=20)
    ax_hr.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_hr.grid(color='gray', linestyle='--', linewidth=0.5)
    mo.center(fig_hr)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ***Rotate the bar plot, sort by rental counts, highlight the daily hours with highest rental counts (over 300), hide redundant axes, and label the bars***
    """)
    return


@app.cell
def _(hr_data, mo, plt):
    # Sort the hourly data frame by total counts
    hr_data_sorted = hr_data.sort_values(by = "mean")

    highlight_colour_hr = '#d95f02'
    non_highlight_colour_hr = '#768493'
    cut_off_hr = 3e2
    hr_data_sorted["colours"] = hr_data_sorted["mean"].apply(lambda x: highlight_colour_hr if x >= cut_off_hr else non_highlight_colour_hr)

    fig_hr_2, ax_hr_2 = plt.subplots(figsize=(18,12))
    bars_hr = plt.barh([f"{_}" for _ in hr_data_sorted["hr"]],
                       hr_data_sorted["mean"], # Set hours as strings so that the axis does not automatically sort the values
                       color = hr_data_sorted["colours"])

    plt.ylabel("Hours", fontsize = 15, labelpad = 15)
    plt.xlabel("Mean hourly rental counts", fontsize = 15, labelpad = 15)

    ax_hr_2.bar_label(bars_hr, fontsize = 15) # Set bar labels
    ax_hr_2.spines[['right', 'top', 'bottom', "left"]].set_visible(False) # Remove all edges
    ax_hr_2.xaxis.set_visible(False) # Remove x-axis

    ax_hr_2.axvline(x=cut_off_hr, zorder=0, color='grey', ls='--', lw=1.5)
    ax_hr_2.text(x=cut_off_hr, y=1, s='300 rented bikes', ha='center', 
            fontsize=22, bbox=dict(facecolor='white', edgecolor='grey', ls='--'))

    ax_hr_2.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_hr_2.grid(color='gray', linestyle='--', linewidth=0.2)

    ax_hr_2.tick_params(axis="both", labelsize=15)

    plt.title("Mean hourly rental counts", fontsize = 22, pad = 15)
    mo.center(fig_hr_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ##*Comment*:
    The mean hourly rent amounts in the two years 2011 and 2012 for hourly periods between 8 AM and 9 AM and between 4 PM and 8 PM exceed 300. A possible explanation is that these are common commute hours, which entail bigger numbers of rented bikes.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
