#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import time

from .. import core, settings, tmux

logger = logging.getLogger(__name__)


def enable():
  text = '-1'
  settings.paths.update.write_text(text)
  logger.debug(f'{settings.paths.update}: <- [{text}]')


def disable():
  text = str(time())
  settings.paths.update.write_text(text)
  logger.debug(f'"{settings.paths.update}" <- [{text}]')


def isEnabled() -> bool:
  if not settings.paths.update.exists():
    logger.debug('"{settings.paths.update}" does not exists, return [True]')
    return True

  text = settings.paths.update.read_text()
  disabled_time = float(text)
  logger.debug(f'"{settings.paths.update}" - read -> [{disabled_time}]')

  if disabled_time == -1:
    # enabled explicitly
    logger.debug('enabled explicitly, return [True]')
    result = True
  else:
    # re-enable after a given time interval
    now = time()
    seconds = now - disabled_time
    logger.debug(f'seconds since last disable: {seconds}')
    result = seconds > settings.maxDisableUpdateInterval
    logger.debug('auto-enabled' if result else 'still disabled')

  return result


def run():
  if not isEnabled():
    logger.warn('o: ✘')
    return
  else:
    logger.debug('o: ✔')
    core.update()
    tmux.respawnFinderWindow()
