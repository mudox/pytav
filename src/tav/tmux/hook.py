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
    result = True
  else:
    # re-enable after a given time interval
    now = time()
    seconds = now - disabled_time
    result = seconds > settings.reenableHookInterval

  return result


def run():
  if not isEnabled():
    logger.debug('hook update ✘')
    return
  else:
    logger.debug('hook update ✔')
    core.update()
    tmux.respawnFinderWindow()

