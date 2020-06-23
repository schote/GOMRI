# Exemplary plot:
# https://gist.github.com/nicoddemus/da4a727aef09de0dd0cfd2d1a6043104

from PyQt5 import QtChart
from warnings import warn


class ExamplePlot(QtChart.QChartView):
    def __init__(self,
                 xData: list,
                 yData: list,
                 xLabel: str,
                 yLabel:str) -> None:

        super(ExamplePlot, self).__init__()

        if len(xData) != len(yData):
            warn("Length of x and y data does not match.")
            return

        series = QtChart.QLineSeries()
        for x, y in zip(xData, yData):
            series.append(x, y)

        self.chart().addSeries(series)
        self.chart().createDefaultAxes()
        self.chart().axisX(series).setTitleText(xLabel)
        self.chart().axisY(series).setTitleText(yLabel)
        self.show()
