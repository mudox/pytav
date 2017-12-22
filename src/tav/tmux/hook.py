#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from time import time

from .. import core, settings, tmux

logger = logging.getLogger(__name__)


def enable():
  line = f'{datetime.now()} | enable\n'
  with settings.paths.update.open('a') as file:
    file.write(line, flush=True)


def disable():
  line = f'{datetime.now()} | {time()}\n'
  with settings.paths.update.open('a') as file:
    file.write(line, flush=True)


def isEnabled() -> '2-tuple: (bool, explain)':
  if not settings.paths.update.exists():
    return True, f'update file ({settings.paths.update}) does not exists'

  lines = settings.paths.update.read_text().strip().splitlines()
  lastLine = lines[-1]
  flag = lastLine.split('|')[1].strip()

  if flag == 'enable':
    return True, 'enalbed explicitly'
  else:
    disabledTime = float(flag)
    timeElapsed = time() - disabledTime
    if timeElapsed > settings.tmux.maxDisableUpdateInterval:
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
