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
    file.write(line)


def disable():
  line = f'{datetime.now()} | {time()}\n'
  with settings.paths.update.open('a') as file:
    file.write(line)


def isEnabled() -> bool:
  if not settings.paths.update.exists():
    logger.debug(f'update file ({settings.paths.update}) does not exists, return ✔')
    return True

  lines = settings.paths.update.read_text()
  lastLine = lines[-1]
  flag = lastLine.split('|')[1].strip()

  if flag == 'enable':
    logger.debug('o:✔  explicitly')
    return True
  else:
    disabledTime = float(flag)
    timeElapsed = time() - disabledTime
    if timeElapsed > settings.maxDisableUpdateInterval:
      logger.debug('o:✔  out of interval')
      return True
    else:
      logger.debug('o:✘  with interval')
      return False


def run():
  if not isEnabled():
    logger.warn('o: ✘')
    return
  else:
    logger.debug('o: ✔')
    core.update()
    tmux.respawnFinderWindow()
