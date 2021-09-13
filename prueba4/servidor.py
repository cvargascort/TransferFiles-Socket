import socket
import struct
import numpy as np
from  pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import json
import time
from sys import exit


#Widget condiguration
app = QtGui.QApplication([])
w = QtGui.QWidget()
layout = QtGui.QGridLayout()
w.setLayout(layout)
w.setWindowTitle("Procesado de señal de audio")
w.setFixedSize(1000, 600)
p = w.palette()
p.setColor(w.backgroundRole(), pg.mkColor('k'))
w.setPalette(p)


pg.setConfigOptions(antialias=True)


class AudioServer():

    HOST = '127.0.0.1'

    def __init__(self, port, layout, w):
        self.port = port

        #Initialize socket connections
        self.socketCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketCon.bind((self.HOST, self.port))
        print("Socket creado:", self.socketCon.getsockname)

        #Initialize Widget layout
        self.lay = layout
        self.labelFps = QtGui.QLabel()
        self.labelFps.setText('Frames per second: 0')
        self.labelFps.setStyleSheet('color: yellow')
        self.plt1 = pg.PlotWidget()
        self.plt2 = pg.PlotWidget()
        self.lay.addWidget(self.labelFps, 0, 0)
        self.lay.addWidget(self.plt1, 1, 0)
        self.lay.addWidget(self.plt2, 1, 1)

        self.fps = 0
        self.timeAnt = 0
        self.timeTcpAnt = 0
        self.w = w

    def listen(self):

        self.socketCon.listen(1)
        print("Escoltant connexions...")
        self.conn, self.addr = self.socketCon.accept()
        print("Connexió acceptada de: ", self.conn.getpeername())

    def readblob(self, size):
        buffer = ""
        while len(buffer) != size:
            print("longitud buffer: ", len(buffer))
            ret = self.conn.recv(size - len(buffer))
            print(ret)
            if not ret:
                raise Exception("Socket closed")
            buffer += ret
        return buffer

    def myreceive(self, size):
        chunks = []
        bytes_recd = 0
        while bytes_recd < size:
            chunk = self.conn.recv(min(size - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def readlong(self):
        size = struct.calcsize("L")
        print(size)
        data = self.myreceive(size)
        print(data)
        print(struct.unpack("L", data))
        return struct.unpack("L", data)

    def checkParam(self, jdata):
        if 'N' in jdata:
            self.N = jdata['N']
        else:
            raise Exception("Incorrect param N in handshake")
        if 'rate' in jdata:
            self.rate = jdata['rate']
        else:
            raise Exception("Incorrect param rate in handshake")
        if 'T' in jdata:
            self.T = jdata['T']
        else:
            raise Exception("Incorrect param T in handshake")

        return True

    def handshake(self):
        longitud = self.readlong()
        print("Longitud....", longitud[0])
        if longitud:
            print("Fent handshake")
            print("Longitud header: ", longitud[0])
            print("LLegint params...")
            data = self.myreceive(longitud[0])
            jdata = json.loads(data.decode('utf-8'))
            print(jdata)
            if self.checkParam(jdata):

                #Enviamos ACK
                ack = 'ACK'
                long = struct.pack("L", len(ack))
                self.conn.sendall(long)
                self.conn.sendall(bytes(ack, 'utf-8'))
                print("Handshake finished correctly")
                self.handshaked = True

            else:
                self.handshaked = False
        else:
            print("No handshake")
            self.handshaked = False

    def initPlot(self):

        self.plt1.setYRange(-20000, 20000)
        self.plt1.getPlotItem().setTitle(title="Representación temporal")
        self.plt1.getAxis('bottom').setLabel('Tiempo')
        self.plt1.getAxis('left').setLabel('Nivel')
        self.plt2.setYRange(0, 2000)
        self.plt2.getPlotItem().setTitle(title="Representación frecuencial (FFT)")
        self.plt2.getAxis('bottom').setLabel('Frecuencia', units='Hz')
        self.plt2.getAxis('bottom').enableAutoSIPrefix(enable=True)
        self.plt2.getAxis('left').setLabel('Nivel')
        self.w.show()

    def receive(self):
        timeTcpAct = time.time()
        print("Temps entre crides receive Tcp: ",
              (timeTcpAct - self.timeTcpAnt) * 1000)
        self.timeTcpAnt = timeTcpAct
        data = self.conn.recv(2 * self.N)
        print("Temps per rebre packets: ", (time.time() - timeTcpAct) * 1000)
        if not data:
            print("no data")
        else:
            #Señal temporal
            count = len(data)/2
            format = "%dh" % (count)
            shorts = struct.unpack(format, data)
            npshorts = np.asarray(shorts)
            xaxis_t = np.linspace(0.0, self.N * self.T, self.N)
            self.plt1.plot(xaxis_t, npshorts, pen=(255, 0, 0), clear=True)

            #Frecuencia
            timeFact = time.time()
            freq = np.fft.rfft(npshorts)
            print("Durada FFT: ",  (time.time() - timeFact) * 1000)
            xaxis_f = np.linspace(0.0, 1.0/(2.0 * self.T), self.N // 2)
            n = int(len(npshorts)/2)
            self.plt2.plot(xaxis_f, (2.0 / self.N) *
                           np.abs(freq[range(n)]), pen=(255, 0, 0), clear=True)

            #Label fps
            timeAct = time.time()
            fps = 1 / (timeAct - self.timeAnt)
            self.timeAnt = timeAct
            self.labelFps.setText('Frames per second: {:2.1f}'.format(fps))


myServer = AudioServer(50007, layout, w)
myServer.listen()
myServer.handshake()
if myServer.handshaked:
    myServer.initPlot()
    timer = QtCore.QTimer()
    timer.timeout.connect(myServer.receive)
    timer.start(0)
else:
    print("No ha estat possible el handshake")
    exit(0)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
