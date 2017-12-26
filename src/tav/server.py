#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import socket
from contextlib import closing
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import exit

from . import core
from .tmux import hook

logger = logging.getLogger(__name__)


def getFreePort():
  with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
    sock.bind(('', 0))
    return sock.getsockname()[1]


def start(port):

  try:
    server = HTTPServer(('', port), HTTPRequestHandler)
    logger.info(f'listening at localhost:{port}')

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
  error_content_type = 'text/plain'

  def do_GET(self):
    logger.debug(f'o:GET {self.path}')

    self._event() or \
        self._stop() or \
        self._invalidPath

  def log_message(self, format, *args):
    if args[1] != '200':
      logger.error(format % tuple(args) + '\n')

  def _invalidPath(self):
    self.send_error(403, 'invalid path')

  #
  # nodes
  #

  def _event(self):
    m = re.match(r'^/event/([^/]+)$', self.path)
    if m is None:
      return False

    else:
      event = m.group(1)

      self.send_response(200)
      self.send_header('Content-Length', 0)
      self.end_headers()

      logger.info(f' [{datetime.now()}] {event}')
      core.onTmuxEvent(event)

      return True

  def _stop(self):
    if self.path != '/stop/':
      return False

    else:
      self.send_response(200)
      self.send_header('Content-Length', 0)
      self.end_headers()

      exit()
