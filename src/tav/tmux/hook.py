#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import time

from .. import core, settings, tmux

logger = logging.getLogger(__name__)


def enable(flag):
  if flag:
    text = '-1'
  else:
    text = str(time())

  settings.paths.hookEnabled.write_text(text)


def is_enabled() -> bool:
  if not settings.paths.hookEnabled.exists():
    return True

  text = settings.paths.hookEnabled.read_text()
  disabled_time = float(text)

  if disabled_time == -1:
    # enabled explicitly
    result = True
  else:
    # re-enable after a given time interval
    now = time()
    seconds = now - disabled_time
    result = seconds > settings.reenableHookInterval

  if settings.verbose:
    print('hook: ' + (result and '✔' or '✘'))

  return result


def run():
  if not is_enabled():
    logger.debug('hook update suppressed')
    return

  core.update()
  tmux.respawnFinderWindow()

