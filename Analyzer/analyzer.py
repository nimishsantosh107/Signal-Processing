import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import struct
import pyaudio
from scipy.fftpack import fft

import sys
import time


class AudioStream(object):
    def __init__(self):

        # pyqtgraph stuff
        pg.setConfigOptions(antialias=True)
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1400, 870)

        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        wf_ylabels = [(0, '0'), (127, '128'), (255, '255')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        sp_xlabels = [(10, '10'), (1000, '1000'), (11025, '11025'), (22050, '22050')]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        self.waveform = self.win.addPlot(
            title='WAVEFORM', row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )
        self.spectrum = self.win.addPlot(
            title='SPECTRUM', row=2, col=1, axisItems={'bottom': sp_xaxis},
        )

        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024 * 1

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )
        # waveform and spectrum x points
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.f = np.linspace(0, self.RATE / 2, self.CHUNK/2)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'waveform':
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setYRange(0, 255, padding=0)
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='g', width=3)
                self.spectrum.setYRange(0, 20000, padding=0.005)
                self.spectrum.setXRange(20, 22050, padding=0.005)

    def update(self):
        wf_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
        wf_data = np.array(struct.unpack(str(2 * self.CHUNK) + 'B', wf_data), dtype='b')[::2]
        self.set_plotdata(name='waveform', data_x=self.x, data_y=wf_data+128,)

        #sp_data = np.abs(sp_data[1:int(self.CHUNK/2)+1]) * 2 / (256 * self.CHUNK)
        sp_data = np.abs(fft(wf_data[0:self.CHUNK]))
        self.set_plotdata(name='spectrum', data_x=self.f, data_y=sp_data[0:self.CHUNK//2])

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()
 

if __name__ == '__main__':

    audio_app = AudioStream()
    audio_app.animation()
