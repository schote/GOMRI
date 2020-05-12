"""
Plot View

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0
@change:    11/05/2020

@summary:   Class for visualization of 1D data in frequency or time domain.

@status:    Under development
@todo:      Implementation, make plot library a parent of this class

"""

import threading
import plotly.graph_objects as go
import pandas as pd


class PlotView(threading):
    """
    Plot view class
    """
    fig = go.Figure()

    def __init__(self) -> None:
        """
        Init plotview class and inherited threading class
        """
        super(threading, self).__init__()

    def run(self, dFrame: pd.DataFrame, flag_rangeSlider: bool = False) -> None:
        """
        Superimposition of threading's run method, that is called, when thread is started
        @param dFrame:              Data frame, with data to be plotted
        @param flag_rangeSlider:    Flag that implies, whether the range slider should be set
        @return:                    None
        """
        # TODO: Get axis from pandas data frame
        for dSet in list(dFrame.columns):
            self.fig.add_trace(go.Scatter(x=list(dFrame.index), y=list(dFrame[dSet])))
        if flag_rangeSlider is not False:
            self.addRangeSlider()
        self.fig.update_layout()
        self.fig.show()

    def addRangeSlider(self) -> None:
        """
        Adds a range slider to the plot
        @return:    None
        """
        # TODO: Setup "rangeselector" dict
        self.fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="YTD",
                             step="year",
                             stepmode="todate"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
