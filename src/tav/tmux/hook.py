#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from time import time

from .. import core, tmux
from .. settings import cfg

logger = logging.getLogger(__name__)


def enable():
  line = f'{datetime.now()} | enable\n'
  with cfg.paths.updateFile.open('a') as file:
    file.write(line)


def disable():
  line = f'{datetime.now()} | {time()}\n'
  with cfg.paths.updateFile.open('a') as file:
    file.write(line)


def isEnabled() -> '2-tuple: (bool, explain)':
  if not cfg.paths.updateFile.exists():
    return True, f'update file ({cfg.paths.updateFile}) does not exists'

  lines = cfg.paths.updateFile.read_text().strip().splitlines()
  lastLine = lines[-1]
  flag = lastLine.split('|')[1].strip()

  if flag == 'enable':
    return True, 'enalbed explicitly'
  else:
    disabledTime = float(flag)
    timeElapsed = time() - disabledTime
    if timeElapsed > cfg.tmux.maxDisableUpdateInterval:
      return True, 'time overdue'
    else:
      return False, 'within interval'


def run():
  enabled, why = isEnabled()
  if not enabled:
    logger.warn(f'o: skip [{why}]')
    return
  else:
    core.update()
    # tmux.respawnFinderWindow()
    tmux.refreshFinderWindow()
