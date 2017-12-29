#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import socket
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from sys import exit

import daemon

from jaclog import jaclog

from . import settings as cfg
from . import core, tmux

logger = logging.getLogger(__name__)


def getFreePort():
  with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
    sock.bind(('', 0))
    return sock.getsockname()[1]


def start(port):
  global logger

  logger.debug('spawn daemon')

  with daemon.DaemonContext():

    jaclog.configure(
        appName='tav', fileName='server.log', printSessionLine=False)
    logger = logging.getLogger(__name__)

    try:
      server = HTTPServer(('', port), HTTPRequestHandler)
      logger.info(f'listening at localhost:{port}')

    except OSError as e:
      if e.errno == 48:
        alternatePort = getFreePort()
        logger.warning(
            f'Port {port} is occupied, try using port {alternatePort}')
        logger.flush()
        server = HTTPServer(('', alternatePort), HTTPRequestHandler)
        logger.info(
            f'Start server listening at localhost:{alternatePort} ...\n\n')
      else:
        raise

    server.serve_forever()


class HTTPRequestHandler(BaseHTTPRequestHandler):

  server_version = 'Tav/0.1'
  protocol_version = 'HTTP/1.1'  # enable persistent connection
  error_content_type = 'text/plain'

  def do_GET(self):
    logger.info(f'o:GET {self.path}')

    for route in [
        self._attach,
        self._hook,
        self._event,
        self._stop,
    ]:
      if route():
        return

    self._invalidPath()

  def log_message(self, format, *args):
    if args[1] != '200':
      logger.error(format % tuple(args) + '\n')

  def _invalidPath(self):
    self.send_error(403, 'invalid path')

  def _sendBare200(self):
    self.send_response(200)
    self.send_header('Content-Length', 0)
    self.end_headers()

  #
  # nodes
  #

  def _event(self):
    m = re.match(r'^/event/([^/]+)/$', self.path)
    if m is None:
      return False

    else:
      self._sendBare200()

      event = m.group(1)
      core.onTmuxEvent(event)

      return True

  def _stop(self):
    if self.path != '/stop/':
      return False

    else:
      self._sendBare200()
      logger.info('server exit')
      exit()

  def _attach(self):
    if self.path != '/attach/':
      return False

    else:
      self._sendBare200()

      tmux.switchTo(cfg.tmux.tavWindowTarget)
      return True

  def _greet(self):
    if self.path != '/hello/tav/':
      return False

    else:
      self._sendBare200()
      return True

  def _hook(self):
    m = re.match(r'^/hook/([^/]+)/([^/]+)/$', self.path)
    if m is None:
      return False

    else:
      self._sendBare200()

      action = m.group(1)
      reason = m.group(2)
      if action == 'enable':
        tmux.hook.enable(reason)
      elif action == 'disable':
        tmux.hook.disable(reason)
      else:
        logger.warning(f'invalid path {self.path}')

      return True
