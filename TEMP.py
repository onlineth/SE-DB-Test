import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
import pandas as pd
import sys
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


def PlotlyPlotPloter(file):

    df = pd.read_csv(file, header=None, delimiter=r"\s+")

    trace1 = Scatter3d(
        x=df[1],
        y=df[2],
        z=df[3],
        mode='lines+markers',
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

PlotlyPlotPloter('double_beta/mctruehits_trk_0.dat')
