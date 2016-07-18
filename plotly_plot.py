import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
import pandas as pd
import cufflinks as cf
import sys
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import math


def PlotlyPlotPloter(file, lines=0):

    cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

    df = pd.read_csv(file, header=None, delimiter=r"\s+")

    if lines:
        mode = 'lines+markers'
    else:
        mode = 'markers'

    trace1 = Scatter3d(
        x=df[1],
        y=df[2],
        z=df[3],
        mode=mode,
        marker=dict(
            size=5,
            sizemode='mm',
            color=df[4],
            colorscale='Viridis',
            colorbar=dict(title='Energy'),
            line=dict(color='rgb(140, 140, 170)')
        )
    )

    data = [trace1]
    layout = dict(height=800, width=1000, title='Plot')
    fig = dict(data=data, layout=layout)
    plot(fig)


# def sortLists(df):
#     # Sorts the list to the next closests point
#     new.tolist() = [df[1][0], df[2][0], df[3][0]]

#     # Start with checking the first point
#     oneToCheck = [df[1][0], df[2][0], df[3][0]]
#     df.drop(0)

#     while 1:
#         distances = [[], []]
#         # Get the smallest distance
#         for i in df:
#             # Find all distance from oneToCheck

#         # Find the smallest value in distances

#         #


#     return newList


# def distance(x, y, z):
#     return math.sqrt((x[1]-x[0])**2 + (y[1]-y[0])**2 + (z[1]-z[0])**2)

PlotlyPlotPloter('single_electron/mctruehits_trk_10508.dat', 1)
