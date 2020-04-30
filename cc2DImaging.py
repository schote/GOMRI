################################################################################
#
#   Author:     David Schote (david.schote@ovgu.de)
#   Date:       01/22/2020
#
#   2D Imaging Sub Application
#   Control center to perform spectrometry, projections and 2D Imaging
#
################################################################################

# import general packages
import time

# import PyQt5 packages
from PyQt5.QtWidgets import QTabWidget
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSignal

# import calculation and plot packages
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from parameters import params
from manager.datamanager import data

CC_2DImag_Form, CC_2DImag_Base = loadUiType('ui/cc2DImag.ui')

class CC2DImagWidget(CC_2DImag_Base, CC_2DImag_Form):

    pe_finished = pyqtSignal()
    call_update = pyqtSignal()
    acq_completed = pyqtSignal()

#_______________________________________________________________________________
#   Init Functions

    def __init__(self):
        super(CC2DImagWidget, self).__init__()
        self.setupUi(self)

        self.data = data()
        self.load_params()
        self.init_seqSelector()

        self.ts = 4

        #self.fig = Figure(); self.fig_canvas = FigureCanvas(self.fig)
        #self.fig.set_facecolor("None")

        #self.mdi = QMdiArea()
        self.tabview = QTabWidget()
        self.tabview.setMovable(True)
        self.tabview.setTabShape(QTabWidget.Rounded)
        self.tabview.setTabPosition(QTabWidget.North)

        self.acq_completed.connect(self.show_Tabs)

        # Connect Frequency input
        self.freq_input.setKeyboardTracking(False)
        self.freq_input.valueChanged.connect(self.data.set_freq)
        self.centerFreq_btn.clicked.connect(self.autocenterFreq)

        # Shim tool
        self.setOffset_btn.clicked.connect(self.set_grad_offsets)

        # Connect start manager button
        self.spectrum_btn.clicked.connect(self.startSpectrum)
        self.startImag_btn.clicked.connect(self.startImaging)
        self.startProj_btn.clicked.connect(self.startProjections)

    def init_seqSelector(self):
        # Disable custom sequence upload
        self.uploadSeq_btn.setVisible(False)
        self.uploadSeq_confirm.setVisible(False)

        #self.seq_selector.currentIndexChanged.connect(self.set_sequence)

        self.seq_selector.addItems(['Spin Echo'])
        #self.seq_selector.setCurrentIndex(0)

    def init_spectrum(self):

        self.imagProgress.setValue(0)

        # Tabview Approach
        # Init Figure
        self.fig = Figure(); self.fig_canvas = FigureCanvas(self.fig)
        self.fig.set_facecolor("None")
        self.tabview.clear()
        self.tabview.addTab(self.fig_canvas, "Spectrum")

        gs = GridSpec(2, 1, figure=self.fig)
        self.freq_ax = self.fig.add_subplot(gs[0,0])
        self.time_ax = self.fig.add_subplot(gs[1,0])
        self.fig_canvas.draw()

        # connect readout finished signal
        try: self.data.readout_finished.disconnect()
        except: pass
        self.data.readout_finished.connect(self.update_spectrum_plot)

    def init_projections(self):

        print("init projection plot.\n")
        self.imagProgress.setValue(0)

        # init figure
        self.fig = Figure(); self.fig_canvas = FigureCanvas(self.fig)
        self.fig.set_facecolor("None")
        self.tabview.clear()
        self.tabview.addTab(self.fig_canvas, "Projections")

        gs = GridSpec(3, 1, figure=self.fig)
        self.Xproj_ax = self.fig.add_subplot(gs[0,0])
        self.Yproj_ax = self.fig.add_subplot(gs[1,0])
        self.Zproj_ax = self.fig.add_subplot(gs[2,0])
        self.fig_canvas.draw()

        self.proj_ax = np.zeros(3)

        if self.proj_x_select.isChecked(): self.proj_ax[0] = 1
        if self.proj_y_select.isChecked(): self.proj_ax[1] = 1
        if self.proj_z_select.isChecked(): self.proj_ax[2] = 1

        # connect readout finished signal
        try: self.data.readout_finished.disconnect()
        except: pass
        self.data.readout_finished.connect(self.update_projection_plot)

        self.call_update.emit()

    def init_imaging(self, npe):

        self.imagProgress.setValue(0)

        # create figures for tab view
        self.IMag_fig = Figure(); self.IMag_canvas = FigureCanvas(self.IMag_fig)
        self.IMag_fig.set_facecolor("None");
        self.IPha_fig = Figure(); self.IPha_canvas = FigureCanvas(self.IPha_fig)
        self.IPha_fig.set_facecolor("None");
        self.kMag_fig = Figure(); self.kMag_canvas = FigureCanvas(self.kMag_fig)
        self.kMag_fig.set_facecolor("None");
        self.kPha_fig = Figure(); self.kPha_canvas = FigureCanvas(self.kPha_fig)
        self.kPha_fig.set_facecolor("None");
        self.kspc_fig = Figure(); self.kspc_canvas = FigureCanvas(self.kspc_fig)
        self.kspc_fig.set_facecolor("None");
        self.sig_fig = Figure(); self.sig_canvas = FigureCanvas(self.sig_fig)
        self.sig_fig.set_facecolor("None")
        self.tabview.clear()

        self.tabview.addTab(self.IMag_canvas, "Magnitude")

        '''
        # add figure tabs to tab view
        self.tabview.addTab(self.sig_canvas, "Signals")
        self.tabview.addTab(self.kspc_canvas, "Overview")
        self.tabview.addTab(self.IMag_canvas, "Magnitude")
        self.tabview.addTab(self.IPha_canvas, "Image Phase")
        self.tabview.addTab(self.kMag_canvas, "k-Space Magnitude")
        self.tabview.addTab(self.kPha_canvas, "k-Space Phase")
        '''

        # add axis to figures in tab view
        self.IMag_ax = self.IMag_fig.add_subplot(111); self.IMag_ax.grid(False); self.IMag_ax.axis(frameon=False)
        self.IMag_canvas.draw(); self.call_update.emit(); self.update()
        self.IPha_ax = self.IPha_fig.add_subplot(111); self.IPha_ax.grid(False); self.IPha_ax.axis(frameon=False)
        #self.IMag_canvas.draw()
        self.kMag_ax = self.kMag_fig.add_subplot(111); self.kMag_ax.grid(False); self.kMag_ax.axis(frameon=False)
        #self.IMag_canvas.draw()
        self.kPha_ax = self.kPha_fig.add_subplot(111); self.kPha_ax.grid(False); self.kPha_ax.axis(frameon=False)
        #self.IMag_canvas.draw()
        gs = GridSpec(2, 2, figure=self.kspc_fig)
        self.kspc_Imag_ax = self.kspc_fig.add_subplot(gs[0,0]); self.kspc_Imag_ax.grid(False);
        self.kspc_Ipha_ax = self.kspc_fig.add_subplot(gs[0,1]); self.kspc_Ipha_ax.grid(False);
        self.kspc_kmag_ax = self.kspc_fig.add_subplot(gs[1,0]); self.kspc_kmag_ax.grid(False); self.kspc_kmag_ax.axis('equal', frameon=False)
        self.kspc_kpha_ax = self.kspc_fig.add_subplot(gs[1,1]); self.kspc_kpha_ax.grid(False); self.kspc_kpha_ax.axis('equal', frameon=False)
        #self.kspc_canvas.draw()
        gs = GridSpec(5, 6, figure=self.sig_fig)
        self.sig_t_ax = self.sig_fig.add_subplot(gs[0,0:6])
        self.sig_f_ax = self.sig_fig.add_subplot(gs[1,0:6])
        self.sig_kmag_ax = self.sig_fig.add_subplot(gs[2:5, 0:3]); self.sig_kmag_ax.grid(False)
        self.sig_Imag_ax = self.sig_fig.add_subplot(gs[2:5, 3:6]); self.sig_Imag_ax.grid(False)
        #self.sig_canvas.draw()

        # init data structures
        # >>> REWORK <<<
        self.buffers_received = 0
        self.kspace_center = 475 # k center time = 1.9*250: echo time is at 1.9ms after acq start
        self.crop_factor = 640#320 #640 # 64 matrix size ~ 640 readout length (need FURTHER CALIBRATION)
        self.crop_size = int(params.npe / 64 * self.crop_factor)#int(params.npe / 64 * self.crop_factor)
        self.half_crop_size = int(self.crop_size / 2)
        self.cntr = int(self.crop_size * 0.99 / 2)
        self.img_mag = np.matrix(np.zeros((npe,npe)))
        self.img_pha = np.matrix(np.zeros((npe,npe)))

        self.ROcrop = int(params.npe*2.5)

        self.kRatio = 2#self.ROcrop*2/params.npe

        '''
        self.k_amp = np.matrix(np.zeros((npe, self.ROcrop*2)))#npe*2)))
        self.k_pha = np.matrix(np.zeros((npe, self.ROcrop*2)))#npe*2)))
        self.kspace = np.matrix(np.zeros((npe, self.ROcrop*2), dtype=np.complex64))#self.crop_size), dtype=np.complex64))
        self.kspace_full = np.matrix(np.zeros((npe, self.ROcrop*2), dtype=np.complex64))#50000), dtype=np.complex64))
        self.full_data = np.matrix(np.zeros(50000))
        '''

        # Old implementation
        #self.kspace_full = np.matrix(np.zeros((npe, self.crop_size), dtype=np.complex64))
        #if npe >= 128: self.kspace = np.matrix(np.zeros((npe, self.crop_size), dtype = np.complex64))
        #else: self.kspace = np.matrix(np.zeros((npe, int(self.crop_size/2)), dtype = np.complex64))
        self.kspace = np.matrix(np.zeros((npe, self.crop_size), dtype = np.complex64))
        self.k_amp = np.matrix(np.zeros((npe, npe*2)))
        self.k_pha = np.matrix(np.zeros((npe, npe*2)))


        # connect readout finished signal
        try: self.data.readout_finished.disconnect()
        except: pass
        self.data.readout_finished.connect(self.processImage)

        #self.call_update.emit()

#_______________________________________________________________________________
#   Control Functions for Spectrum, Projection or Image Acquisition

    def autocenterFreq(self):
        if self.data.center_freq != 'nan':
            self.freq_input.setValue(round(self.data.center_freq,5))
            self.data.set_freq(self.data.center_freq)
            self.data.acquire

    def startSpectrum(self):
        self.data.set_SE()
        self.data.change_TE(10)
        self.init_spectrum()
        self.data.acquire

    def startImaging(self):

        params.npe = self.npe_input.value()
        if self.tr_input.value() >= 1050: params.TR = self.tr_input.value()-1000
        else: params.TR = 1050
        params.avg_img = self.avg_input.value()

        self.data.set_2dSE()
        #self.data.set_SE()
        #self.data.change_TE(10)
        self.data.set_freq(params.freq)
        self.data.set_at(params.at)

        self.init_imaging(params.npe)

        self.disable_ui()
        self.data.acquireImage(params.npe, params.TR, self.ts)

        '''
        for acqCount in range(params.avg_img):
            print("Averaging cycle: {}/{}".format(acqCount, params.avg_img))
            self.data.acquireImage(params.npe, params.TR)
            # Store image (3D array) or calculate moving avg
            # call init_imaging
        '''

    def startProjections(self):

        self.init_projections()
        self.disable_ui()
        #self.proj_ax = 0

        print("self.proj_ax: {}".format(self.proj_ax))

        # performs all 3 projections
        for idx in range(3):
            #time.sleep(4)
            #self.data.acquireProjection(idx)
            print("AX:\t{}".format(self.proj_ax[idx]))

            if self.proj_ax[idx] != 0:
                time.sleep(4)
                self.data.acquireProjection(idx)

            #print("Projection axis: ", ax)

        self.enable_ui()

    def set_sequence(self, idx):

        # switch case for changed sequence
        seq = {
            0: self.data.set_2dSE,
            1: print(" ")#print("Not implemented jet.\n")
        }
        seq[idx]()

    def set_grad_offsets(self):

        params.grad[0] = self.xOffset_input.value()
        params.grad[1] = self.yOffset_input.value()
        params.grad[2] = self.zOffset_input.value()
        params.grad[3] = self.z2Offset_input.value()

        self.data.set_gradients(params.grad[0], params.grad[1], params.grad[2], params.grad[3])

    def processImage(self):
        idx = self.ts*250 # 1 sample = 4us, ts = 4ms -> idx = 1000 samples
        data = self.data.data#*2000.0
        dclip = data[0:idx]
        self.freqaxis = np.linspace(-125000, 125000, idx) # 1000 datapoints
        self.timeaxis = np.linspace(0, self.ts, idx) # 4ms
        self.mag = np.abs(dclip)
        self.pha = np.angle(dclip)
        self.real = np.real(dclip)
        self.imag = np.imag(dclip)

        self.fft_mag = abs(np.fft.fftshift(np.fft.fft(np.fft.fftshift(dclip), n=idx, norm='ortho')))

        #self.kspace_full[self.buffers_received, :] = data[0:self.crop_size]
        #self.kspace_full[self.buffers_received, :] = dclip[self.kspace_center-self.ROcrop:self.kspace_center+self.ROcrop]#data
        #self.full_data = np.vstack([self.full_data, data])

        self.k_amp[self.buffers_received, :] = np.abs(data[self.kspace_center - params.npe : self.kspace_center + params.npe])#mag[self.kspace_center - params.npe : self.kspace_center + params.npe]
        self.k_pha[self.buffers_received, :] = np.angle(data[self.kspace_center - params.npe : self.kspace_center + params.npe])#pha[self.kspace_center - params.npe : self.kspace_center + params.npe]

        #self.k_amp[self.buffers_received, :] = self.mag[self.kspace_center-self.ROcrop:self.kspace_center+self.ROcrop]#[self.kspace_center-params.npe : self.kspace_center+params.npe]
        #self.k_pha[self.buffers_received, :] = self.pha[self.kspace_center-self.ROcrop:self.kspace_center+self.ROcrop]#[self.kspace_center-params.npe : self.kspace_center+params.npe]
        #k_amp_1og10 = np.log10(self.k_amp)

        #if params.npe >= 128: self.kspace[self.buffers_received, :] = data[0:self.crop_size]
        #else: self.kspace[self.buffers_received, :] = data[0:int(self.crop_size/2)]

        self.kspace[self.buffers_received, :] = data[0:self.crop_size]

        #if params.npe >= 128: self.kspace = self.kspace_full[0:params.npe, :]
        #else: self.kspace = self.kspace_full[0:params.npe, 0:int(self.crop_size/2)]

        #self.kspace = self.kspace_full[0:params.npe, :]#self.kspace_center-self.half_crop_size:self.kspace_center+self.half_crop_size]
        Y = np.fft.fftshift(np.fft.fft2(np.fft.fftshift(self.kspace)))

        self.img_mag = np.abs(Y[:, self.cntr-int(params.npe/2-1):self.cntr+int(params.npe/2+1)])
        self.img_pha = np.angle(Y[:, self.cntr-int(params.npe/2-1):self.cntr+int(params.npe/2+1)])

        self.buffers_received += 1
        if self.buffers_received == params.npe:
            self.acq_completed.emit()
            self.enable_ui()

        #print("{}/{} received".format(self.buffers_received, params.npe))
        self.imagProgress.setValue(100*self.buffers_received/params.npe)
        #self.call_update.emit()

        self.update_imaging_plot()

#_______________________________________________________________________________
#   Function to Update the plots

    def update_spectrum_plot(self):

        self.freq_ax.clear(); self.fig_canvas.draw()
        self.freq_ax.plot(self.data.freqaxis[int(self.data.data_idx/2 - self.data.data_idx/10):int(self.data.data_idx/2 + self.data.data_idx/10)],
            self.data.fft_mag[int(self.data.data_idx/2 - self.data.data_idx/10):int(self.data.data_idx/2 + self.data.data_idx/10)]/max(self.data.fft_mag))
        self.fig_canvas.draw();
        self.time_ax.clear()
        self.time_ax.plot(self.data.time_axis, self.data.mag_t, label='Magnitude'); self.fig_canvas.draw()
        self.time_ax.plot(self.data.time_axis, self.data.real_t, label='Real'); self.fig_canvas.draw()
        self.time_ax.plot(self.data.time_axis, self.data.imag_t, label='Imaginary'); self.fig_canvas.draw()
        self.time_ax.legend()

        '''
        self.freq_canvas.draw()
        self.freq_w.update()
        self.time_canvas.draw()
        self.time_w.update()
        '''

        self.fig_canvas.draw()
        self.call_update.emit()

    def update_projection_plot(self):
        print("Update plot.\n")

        # implement if-statement (dependent on self.proj_ax for plot)
        if self.proj_ax[0] == 1:
            self.Xproj_ax.plot(self.data.fft_mag); self.fig_canvas.draw()
            self.proj_ax[0] = 0
        elif self.proj_ax[1] == 1:
            self.Yproj_ax.plot(self.data.fft_mag); self.fig_canvas.draw()
            self.proj_ax[1] = 0
        elif self.proj_ax[2] == 1:
            self.Zproj_ax.plot(self.data.fft_mag); self.fig_canvas.draw()
            self.proj_ax[2] = 0

        #self.fig_canvas.draw()
        self.call_update.emit()

    def update_imaging_plot(self):

        self.IMag_ax.imshow(self.img_mag, cmap='gray')
        self.IMag_ax.axis('off')
        self.IMag_canvas.draw()

        self.call_update.emit()
        self.update()

        '''
        self.IMag_ax.imshow(self.img_mag, cmap='gray'); self.IMag_ax.axis('off')
        self.IMag_canvas.draw(); self.call_update.emit()

        self.IPha_ax.imshow(self.img_pha, cmap='gray'); self.IPha_ax.axis('off')
        self.IPha_canvas.draw(); self.call_update.emit()

        self.kMag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.kMag_ax.axis('off')
        self.kMag_canvas.draw(); self.call_update.emit()

        self.kPha_ax.imshow(self.k_pha, cmap='inferno', aspect=self.kRatio); self.kPha_ax.axis('off')
        self.kPha_canvas.draw(); self.call_update.emit()

        self.kspc_Imag_ax.imshow(self.img_mag, cmap='gray'); self.kspc_Imag_ax.axis('off'); self.kspc_canvas.draw()
        self.kspc_Ipha_ax.imshow(self.img_pha, cmap='gray'); self.kspc_Ipha_ax.axis('off'); self.kspc_canvas.draw()
        self.kspc_kmag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.kspc_kmag_ax.axis('off'); self.kspc_canvas.draw()
        self.kspc_kpha_ax.imshow(self.k_pha, cmap='inferno', aspect=self.kRatio); self.kspc_kpha_ax.axis('off'); self.kspc_canvas.draw()
        self.call_update.emit()

        self.sig_f_ax.clear(); self.sig_t_ax.clear(); self.sig_canvas.draw()
        self.sig_f_ax.plot(self.freqaxis, self.fft_mag); self.sig_canvas.draw()
        self.sig_t_ax.plot(self.timeaxis, self.mag, label='Magnitude'); self.sig_canvas.draw()
        self.sig_t_ax.plot(self.timeaxis, self.real, label='Real'); self.sig_canvas.draw()
        self.sig_t_ax.plot(self.timeaxis, self.imag, label='Imaginary'); self.sig_canvas.draw()
        self.sig_t_ax.legend()
        self.sig_Imag_ax.imshow(self.img_mag, cmap='gray'); self.sig_Imag_ax.axis('off'); self.sig_canvas.draw()
        self.sig_kmag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.sig_kmag_ax.axis('off'); self.sig_canvas.draw()
        self.sig_canvas.draw(); self.call_update.emit()
        '''

    def show_Tabs(self):

        self.IMag_ax.imshow(self.img_mag, cmap='gray'); self.IMag_ax.axis('off')
        self.IPha_ax.imshow(self.img_pha, cmap='gray'); self.IPha_ax.axis('off')
        self.kMag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.kMag_ax.axis('off')
        self.kPha_ax.imshow(self.k_pha, cmap='inferno', aspect=self.kRatio); self.kPha_ax.axis('off')
        self.kspc_Imag_ax.imshow(self.img_mag, cmap='gray'); self.kspc_Imag_ax.axis('off')
        self.kspc_Ipha_ax.imshow(self.img_pha, cmap='gray'); self.kspc_Ipha_ax.axis('off')
        self.kspc_kmag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.kspc_kmag_ax.axis('off')
        self.kspc_kpha_ax.imshow(self.k_pha, cmap='inferno', aspect=self.kRatio); self.kspc_kpha_ax.axis('off')
        self.sig_f_ax.clear(); self.sig_t_ax.clear()
        self.sig_f_ax.plot(self.freqaxis, self.fft_mag)
        self.sig_t_ax.plot(self.timeaxis, self.mag, label='Magnitude')
        self.sig_t_ax.plot(self.timeaxis, self.real, label='Real')
        self.sig_t_ax.plot(self.timeaxis, self.imag, label='Imaginary')
        self.sig_t_ax.legend()
        self.sig_Imag_ax.imshow(self.img_mag, cmap='gray'); self.sig_Imag_ax.axis('off')
        self.sig_kmag_ax.imshow(self.k_amp, cmap='inferno', aspect=self.kRatio); self.sig_kmag_ax.axis('off')

        self.sig_canvas.draw()
        self.kspc_canvas.draw()
        self.IMag_canvas.draw()
        self.IPha_canvas.draw()
        self.kMag_canvas.draw()
        self.kPha_canvas.draw()

        self.tabview.clear()
        self.tabview.addTab(self.sig_canvas, "Signals")
        self.tabview.addTab(self.kspc_canvas, "Overview")
        self.tabview.addTab(self.IMag_canvas, "Magnitude")
        self.tabview.addTab(self.IPha_canvas, "Image Phase")
        self.tabview.addTab(self.kMag_canvas, "k-Space Magnitude")
        self.tabview.addTab(self.kPha_canvas, "k-Space Phase")

#_______________________________________________________________________________
#   Disable and Enable User Interface

    def disable_ui(self):
        self.seq_input_widget.setEnabled(False)
        self.grad_offset_widget.setEnabled(False)
        self.startImag_btn.setEnabled(False)
        self.proj_select_widget.setEnabled(False)
        self.startProj_btn.setEnabled(False)
        self.setOffset_btn.setEnabled(False)
        self.specBtn_widget.setEnabled(False)
        self.avg_input.setEnabled(False)

    def enable_ui(self):
        self.seq_input_widget.setEnabled(True)
        self.grad_offset_widget.setEnabled(True)
        self.startImag_btn.setEnabled(True)
        self.proj_select_widget.setEnabled(True)
        self.startProj_btn.setEnabled(True)
        self.setOffset_btn.setEnabled(True)
        self.specBtn_widget.setEnabled(True)
        self.avg_input.setEnabled(True)
#_______________________________________________________________________________
#   Load/Save Parameters

    def load_params(self):
        self.npe_input.setValue(params.npe)
        self.freq_input.setValue(params.freq)
        self.tr_input.setValue(params.TR)
        self.xOffset_input.setValue(params.grad[0])
        self.yOffset_input.setValue(params.grad[1])
        self.zOffset_input.setValue(params.grad[2])
        self.z2Offset_input.setValue(params.grad[3])

    def saveData(self, path_str):
        data = pd.DataFrame(self.kspace)
        with open(path_str,'w') as file:
            file.write(data.to_csv())
