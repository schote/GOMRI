"""
Operations Namespace

@author:    David Schote
@contact:   david.schote@ovgu.de
@version:   1.0
@change:    06/28/2020

@summary:

"""

class Namespace:
    systemproperties = "System Properties"
    frequency = "Frequency"
    attenuation = "Attenuation"
    sampletime = "Sample Time"
    shim = "Gradient Shim Values"
    x_grad = "X Gradient"
    y_grad = "Y Gradient"
    z_grad = "Z Gradient"
    z2_grad = "Z² Gradient"
    sequence = "sequence"
    sqncproperties = "Sequence Properties"
    type = "Acquisition Type"


class AcquisitionTypes:
    spectrum = "Spectrum"
    projection = "Projection"
    kspace = "k-Space"