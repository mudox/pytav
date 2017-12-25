#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .. import core, tmux
from .agent import _getStdout, _run

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
    f'{event} -> run-shell "curl http://localhost:10086/event/{event}"'
    for event in _events
]


def enable():
  logger.info('enable hooking')
  cmds = [
      f'''
      tmux set-hook -g {event} "run-shell 'curl http://localhost:10086/event/{event}'"
      ''' for event in _events
  ]
  cmds = '\n'.join(cmds)
  _run(cmds)


def disable():
  logger.info('disable hooking')
  cmds = [f'tmux set-hook -gu {event}' for event in _events]
  cmds = '\n'.join(cmds)
  _run(cmds)


def isEnabled():
  out = _getStdout('tmux show-hooks -g')
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


def run():
  core.update()
  tmux.refreshTavWindow()
