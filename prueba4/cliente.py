import pyaudio
import struct
import time
import socket
import json


class AudioRecorder():
    host = '127.0.0.1'
    port = 50007
    N = 4096  # chunk
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    T = 1/rate

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.host, self.port))

    def myreceive(self, size):
        chunks = []
        bytes_recd = 0
        while bytes_recd < size:
            chunk = self.sock.recv(min(size - bytes_recd, 2048))
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

    def handshake(self):
        #Enviamos parametros al servidor
        param = {
            "N": self.N,
            "rate": self.rate,
            "T": self.T,
            "channels": self.channels,
            "format": self.format
        }

        paramSer = json.dumps(param)
        long = struct.pack("L", len(paramSer))
        self.sock.sendall(long)
        self.sock.sendall(bytes(paramSer, 'utf-8'))
        #Recibimos ACK
        longitud = self.readlong()
        if longitud:
            data = self.myreceive(longitud[0])
            if data.decode('utf-8') == 'ACK':
                print("Handshake finished correctly")
                self.handshaked = True
            else:
                self.handshaked = False

    def callbackFunc(self, in_data, frame_count, time_info, status_flags):
        print("Callback...")
        self.sock.sendall(in_data)
        return (in_data, pyaudio.paContinue)

    def openStream(self):
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.N,
                                  stream_callback=self.callbackFunc)

    def initStream(self):
        self.stream.start_stream()
        while self.stream.is_active():
            time.sleep(1)
            
