#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from time import time

import core
import settings


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
    return
  else:
    core.update()
    subprocess.run(['tmux', 'respawn-window', '-k',
                    '-t', settings.finderWindowTarget])
