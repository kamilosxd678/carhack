import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web

ioloop = tornado.ioloop.IOLoop.instance()

logging.basicConfig(level=0)
log = logging.getLogger('carapp')

log.info("test")

import can
import web
import camera
import data

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, app):
        self.app = app

    def get(self):
        self.write(unicode(web.index(self)))


class CarApp(object):
    def __init__(self):
        log.info('starting app')
        self.start = time.time()

        self.basename = 'logs/counters/%s/' % time.strftime('%Y-%m-%d.%H.%M.%S')
        self.counters = {}

        self.can = can.CAN(logging=True, simulate=False)

        # self.cam = camera.Webcam(self)
        # self.cam.start()

        self.obd2 = can.OBD2(self, self.can)

        # self.car =

        # def read(frame):
        #     print frame
        # self.can.subscribe(read)

    def add_counter(self, name, format, description):
        counter = data.TimeSeries(name, format, self.basename)
        counter.description = description
        self.counters[name] = counter
        return counter

    def run(self):
        self.tornadoapp = tornado.web.Application([
            (r'/static/(.*)',   tornado.web.StaticFileHandler, dict(path='static')),
            (r'/cam.jpg',       web.WebcamHandler,   dict(app=self)),
            (r'/echo',          web.EchoSocket,      dict(app=self)),
            (r'/can',           web.CanSocket,       dict(app=self)),
            (r'/',              MainHandler,         dict(app=self)),
        ])

        self.http_server = tornado.httpserver.HTTPServer(self.tornadoapp)
        self.http_server.listen(8001)

        # block forever
        try:
            log.info('Starting mainloop. Press ^C to exit')
            ioloop.start()
        except KeyboardInterrupt:
            log.info('Exiting')
            self.can.close()

if __name__ == '__main__':
    app = CarApp()

    app.can.simulate(can.CANLog('canlog.2012-10-08.19.13.11.log'))

    app.run()
