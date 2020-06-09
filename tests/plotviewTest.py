from manager.acquisitionmanager import AcquisitionManager as acqMngr
from plotview import PlotView as pltView
import pandas as pd

data = acqMngr.get_exampleFidData()

dataObj = \
    {
        'fft': data.f_fftMagnitude,
        'time': data.t_magnitude
    }

dFrame = pd.DataFrame(data=dataObj)
pltView.run(dFrame, False)
