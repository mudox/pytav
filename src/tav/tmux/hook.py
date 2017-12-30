#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from contextlib import contextmanager

from .. import shell

logger = logging.getLogger(__name__)

_events = [
    'window-linked',
    'window-renamed',
    'window-unlinked',
    'session-created',
    'session-renamed',
    'session-closed',
]

_expect = [
    f'{eventName} -> run-shell "tav event {eventName}"'
    for eventName in _events
]


def enable(reason):
  logger.info(f'o:{reason}')

  cmds = [
      f'''
      tmux set-hook -g {eventName} "run-shell 'tav event {eventName}'"
      ''' for eventName in _events
  ]
  cmds = '\n'.join(cmds)
  shell.run(cmds)


def disable(reason):
  logger.info(f'o:{reason}')

  cmds = [f'tmux set-hook -gu {event}' for event in _events]
  cmds = '\n'.join(cmds)
  shell.run(cmds)


@contextmanager
def reenable(reason):
  try:
    disable('before ' + reason)
    yield
  finally:
    enable('after ' + reason)


def isEnabled():
  out = shell.getStdout('tmux show-hooks -g')
  if out is None:
    return False
  else:
    out = out.strip().splitlines()

  for line in _expect:
    if line not in out:
      print(line)
      return False
  else:
    return True
