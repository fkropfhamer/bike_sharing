import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo, np, plt):
    x = np.random.randn(500)
    y = np.random.randn(500)

    fig, ax = plt.subplots()

    fig.savefig("./plots/scatter.png")
    ax.scatter(x, y)
    ax = mo.ui.matplotlib(plt.gca())
    ax
    return


if __name__ == "__main__":
    app.run()
