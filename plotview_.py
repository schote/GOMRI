"""
Plot View

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   2.0
@change:    11/05/2020

@summary:   Class for visualization of 1D data in frequency or time domain.

@status:    Under development
@todo:      Plotview class with matplotlib, test threading

"""

import threading
from matplotlib.axes import Axes
import pandas as pd


class SpectrumPlot(threading):
    """
    Plot view class
    """
    def __init__(self) -> None:
        """
        Init plotview class and inherited threading class
        """
        super(threading, self).__init__()

    @staticmethod
    def run(dFrame: pd.DataFrame) -> Axes:
        """
        Superimposition of threading's run method, that is called, when thread is started
        @param dFrame:              Data frame, with data to be plotted
        @return:                    None
        """
        ax = Axes()
        for dSet in list(dFrame.columns):
            ax.plot(list(dFrame.index), list(dFrame[dSet]))

        return ax
