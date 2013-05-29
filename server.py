#!/usr/bin/env python
# --encoding: utf-8--

import os
import sys
import signal
import socket

from tornado import ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer


class iApplication(Application):
    """
    Settings and URL router.
    """
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]
        
        Application.__init__(self, handlers)


class WebHandler(RequestHandler):
    def compute_etag(self):
        return


class MainHandler(WebHandler):
    def get(self):
        self.redirect("https://github.com/shelmesky?tab=repositories", permanent=True)


#make current process goto daemon
def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir(".") 
    os.umask(0) 
    os.setsid() 

    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Now I am a daemon!
    
    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def server_stop():
    '''
    停止服务器并做一些清理工作
    '''
    ioloop.IOLoop.instance().stop()
    redis.SignalHandlerManager.on_server_exit()


def handler_signal(signum, frame):
    # if process receive SIGNINT/SITTERM/SIGQUIT
    # stop the server
    if signum == 2 or signum == 3 or signum ==15:
        LOG.error("Receive signal: %s" % signum)
        LOG.error("Server quit.")
        server_stop()
    elif signum == 14:  # ignore SIGALARM
        pass


signal.signal(signal.SIGTERM, handler_signal)
signal.signal(signal.SIGINT, handler_signal)
signal.signal(signal.SIGQUIT, handler_signal)
signal.signal(signal.SIGALRM, handler_signal)


def main(port):
    reload(sys)
    sys.setdefaultencoding('UTF-8')
    app = iApplication()
    # xheaders=True
    # tronado运行在reverse proxy后面的时候获取client真实IP
    server = HTTPServer(app, xheaders=True)
    server.bind(port, family=socket.AF_INET)
    server.start()
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main(8001)

