#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import socket
import sys
from contextlib import closing, suppress
from http.server import BaseHTTPRequestHandler, HTTPServer

from jaclog.formatter import Formatter

# configure logging
rootLogger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(Formatter())
rootLogger.addHandler(handler)
rootLogger.setLevel(logging.NOTSET)

logger = logging.getLogger('tav.server')


def getFreePort():
  with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
    sock.bind(('', 0))
    return sock.getsockname()[1]


def start(port):

  try:
    server = HTTPServer(('', port), HTTPRequestHandler)
    logger.info(f'Start server listening at localhost:{port} ...\n\n')

  except OSError as e:
    if e.errno == 48:
      alternatePort = getFreePort()
      logger.warning(f'Port {port} is occupied, try using port {alternatePort}')
      logger.flush()
      server = HTTPServer(('', alternatePort), HTTPRequestHandler)
      logger.info(f'Start server listening at localhost:{alternatePort} ...\n\n')
    else:
      raise

  server.serve_forever()


class HTTPRequestHandler(BaseHTTPRequestHandler):
  server_version = 'Tav/0.1'
  protocol_version = 'HTTP/1.1'  # enable persistent connection

  def do_GET(self):
    m = re.match(r'^/event/([^/]+)$', self.path)
    if m is not None:
      self.newEvent(m.group(1))
    else:
      self.send_error(
          403,
          'Invalid API path',
          '''
          Currently JackServeronly support:

            - POST /session/ HTTP/1.1
              Notify of a new Xcode project running session

            - POST /event/   HTTP/1.1
              Send a new event
          '''
      )
      return

  def newEvent(self, event):
    self.send_response(200)
    self.send_header('Content-Length', 0)
    self.end_headers()

    logger.debug(f'new event: {event}')

  def log_message(self, format, *args):
    if args[1] != '200':
      logger.error(format % tuple(args) + '\n')


if __name__ == "__main__":
  with suppress(KeyboardInterrupt):
    start(10086)
