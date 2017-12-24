#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from importlib import import_module
from pathlib import Path

from jaclog import jaclog


def _initLogging():
  # get logging tty if any
  # TODO!: use file to read and parse to get the log winder target, DO NOT import settings
  cmdstr = f'''
    tmux list-panes -t "Tav:Log" -F '#{{pane_tty}}'
  '''

  tty = None
  ttyLog = None
  p = sp.run(cmdstr, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
  if p.returncode != 0:
    ttyLog = f'error searching logging tty: {p.stderr.decode()}'
  else:
    tty = p.stdout.decode().strip().splitlines()[0]

  jaclog.configure(
      appName='tav',
      logTTY=tty,
      compact=True
  )

  logger = logging.getLogger(__name__)

  # log tty searching error if any
  if ttyLog is not None:
    logger.warning(ttyLog)

  # WARNING: must be put after `jaclog.configure`
  cfg = import_module('tav.settings').cfg
  if tty is not None:
    cfg.tmux.logTTY = Path(tty)

_initLogging()
