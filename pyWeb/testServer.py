import sys
import json
import socketserver
import socket
import math
import io
import matplotlib.pyplot as plt
import oopgui

from easyHTTP import EasyHTTPHandler, EasyHTTPServer, EasyHTTPServerThreaded

Globals = {}

class TestAppHandler (EasyHTTPHandler):
    def echo (self, req, qstr):
        return self.response (json.dumps(qstr), self.PlainTextType)

    def callme (self, req, qstr):
        return self.response("called me", self.HTMLType)

    def get (self, req, qstr):
        global Globals
        return self.response(json.dumps(Globals), self.PlainTextType)

    def set (self, req, qstr):
        global Globals
        Globals.update (qstr)
        return self.response("done", self.HTMLType)

    def fileupload(self, req, qstr):
        return self.response(qstr['content'][0], self.PlainTextType)

    def echoJpeg(self, req, qstr):
        imgContent = qstr.get('imgcontent')
        if not imgContent:
            return None, ""

        imgData = imgContent[0]
        return self.response(imgData, "image/jpeg")

    def getResult(self, req, qstr):
        paramA = self.floatVal(qstr, 'paramA', 1)
        paramB = self.floatVal(qstr, 'paramB', 1)
        result = {'result': (paramA + paramB) }
        return self.response(json.dumps(result), self.PlainTextType)

    def getImage(self, req, qstr):
        fig = plt.figure(figsize=(4,4))
        length, freq = self.intVal(qstr, 'paramL', 1), self.floatVal(qstr, 'paramF', 1)
        xdata = range(length * 100)
        data = [ math.sin(freq*x/50*math.pi) for x in xdata ]
        plt.plot (xdata, data, 'r-')
        imgData = io.BytesIO()
        fig.savefig(imgData, format='png')
        plt.close(fig)
        imgData.seek(0);
        buf = imgData.read()
        return self.response(buf, 'image/png')

    def drawgui(self, req, qstr):
        self.oop.update(qstr)
        imgData = io.BytesIO()
        self.oop.fig.savefig(imgData, format='png')
        imgData.seek(0)
        buf = imgData.read()
        return self.response(buf, 'image/png')

    def save_to_db(self, req, qstr):
        self.oop.update(qstr)
        self.oop.save_to_db()
        return(json.dumps("File saved to db"), self.PlainTextType)

    def save_to_file(self, req, qstr):
        self.oop.update(qstr)
        self.oop.save_to_file()
        return(json.dumps("File saved to disk"), self.PlainTextType)


if __name__ == "__main__":
    import signal
    import os

    def terminate(signum, frame):
        print ("SIGINT, terminated")
        os._exit(os.EX_OK)

    signal.signal (signal.SIGINT, terminate)
    try:
        port = int(sys.argv[1])
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print ("HTTPD server started", hostname, ip, port)

        TestAppHandler.DocRoot = "docs"
        TestAppHandler.logEnabled = True
        TestAppHandler.oop = oopgui.Oopgui()
        ts = EasyHTTPServer (('', port), TestAppHandler)
        ts.run4ever()
    except Exception as e:
        print (e)

