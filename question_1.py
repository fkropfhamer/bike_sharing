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

    return FixedLocator, pd, plt


@app.cell
def _(pd):
    # Read data
    # ---------

    data_day = pd.read_csv("day.csv")
    data_hr = pd.read_csv("hour.csv")

    weekday_data = data_day.groupby(data_day["weekday"])["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    mnth_data = data_day.groupby(data_day["mnth"])["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    yr_data = data_day.groupby(data_day["yr"])["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    hr_data = data_hr.groupby(data_hr["hr"])["cnt"].agg(mean="mean", median="median", n="count").reset_index()
    return hr_data, mnth_data, weekday_data, yr_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Rental counts in weekdays**
    """)
    return


@app.cell
def _(plt, weekday_data):
    fig_weekday, ax_weekday = plt.subplots(figsize=(8,6))
    ax_weekday.spines[['right', 'top']].set_visible(False)
    plt.bar(weekday_data["weekday"], weekday_data["mean"])
    plt.xlabel("Weekdays")
    plt.ylabel("Mean daily rental counts")
    plt.title("Mean daily rental counts in weekdays", fontsize = 15)
    ax_weekday.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_weekday.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
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
def _(mnth_data, plt):
    fig_mnth, ax_mnth = plt.subplots(figsize=(8,6))
    ax_mnth.spines[['right', 'top']].set_visible(False)
    plt.bar(mnth_data["mnth"], mnth_data["mean"])
    plt.xlabel("Months")
    plt.ylabel("Mean daily rental counts")
    plt.title("Mean daily rental counts in months", fontsize = 15)
    ax_mnth.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_mnth.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ***Highlight months with high mean daily rental counts (over 5000)***
    """)
    return


@app.cell
def _(mnth_data, plt):
    highlight_colour_mnth = '#d95f02'
    non_highlight_colour_mnth = '#768493'
    cut_off_mnth = 5000
    mnth_data_copy = mnth_data.copy()
    mnth_data_copy["colours"] = mnth_data_copy["mean"].apply(lambda x: highlight_colour_mnth if x >= cut_off_mnth else non_highlight_colour_mnth)

    fig_mnth_2, ax_mnth_2 = plt.subplots(figsize=(8,6))
    ax_mnth_2.spines[['right', 'top']].set_visible(False)

    plt.bar(mnth_data_copy["mnth"], mnth_data_copy["mean"], color = mnth_data_copy["colours"])
    plt.xlabel("Months")
    plt.ylabel("Mean daily rental counts")
    plt.title("Mean daily rental counts in months", fontsize = 15)
    ax_mnth_2.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_mnth_2.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
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
def _(FixedLocator, plt, yr_data):
    fig_yr, ax_yr = plt.subplots(figsize=(8,6))
    ax_yr.spines[['right', 'top']].set_visible(False)
    plt.bar(yr_data["yr"]+2011, yr_data["mean"])
    plt.gca().xaxis.set_major_locator(FixedLocator([2011,2012])) # Define fixed point on x-axis
    plt.xlabel("Years")
    plt.ylabel("Mean daily rental counts")
    plt.title("Mean daily rental counts in years", fontsize = 15)
    ax_yr.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_yr.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
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
def _(hr_data, plt):
    fig_hr, ax_hr = plt.subplots(figsize=(8,6))
    ax_hr.spines[['right', 'top']].set_visible(False)

    plt.bar(hr_data["hr"], hr_data["mean"])
    plt.xlabel("Hours")
    plt.ylabel("Mean hourly rental counts")
    plt.title("Mean hourly rental counts", fontsize = 15)
    ax_hr.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    ax_hr.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### ***Rotate the bar plot, sort by rental counts, highlight the daily hours with highest rental counts (over 300), hide redundant axes, and label the bars***
    """)
    return


@app.cell
def _(hr_data, plt):
    # Sort the hourly data frame by total counts
    hr_data_sorted = hr_data.sort_values(by = "mean")

    highlight_colour_hr = '#d95f02'
    non_highlight_colour_hr = '#768493'
    cut_off_hr = 3e2
    hr_data_sorted["colours"] = hr_data_sorted["mean"].apply(lambda x: highlight_colour_hr if x >= cut_off_hr else non_highlight_colour_hr)

    fig_hr_2, ax_hr_2 = plt.subplots(figsize=(12,8))
    bars_hr = plt.barh([f"{_}" for _ in hr_data_sorted["hr"]],
                       hr_data_sorted["mean"], # Set hours as strings so that the axis does not automatically sort the values
                       color = hr_data_sorted["colours"])

    plt.ylabel("Hours")
    plt.xlabel("Mean hourly rental counts")

    ax_hr_2.bar_label(bars_hr) # Set bar labels
    ax_hr_2.spines[['right', 'top', 'bottom', "left"]].set_visible(False) # Remove all edges
    ax_hr_2.xaxis.set_visible(False) # Remove x-axis

    ax_hr_2.axvline(x=cut_off_hr, zorder=0, color='grey', ls='--', lw=1.5)
    ax_hr_2.text(x=cut_off_hr, y=1, s='300 rented bikes', ha='center', 
            fontsize=14, bbox=dict(facecolor='white', edgecolor='grey', ls='--'))

    # ax_hr_2.set_axisbelow(True) # Ensures grid lines are drawn below other elements
    # ax_hr_2.grid(color='gray', linestyle='--', linewidth=0.5)

    plt.title("Mean hourly rental counts", fontsize = 15)
    plt.show()
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
