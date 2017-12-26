#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

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
    f'{eventName} -> run-shell "tavs event {eventName}"'
    for eventName in _events
]


def enable(reason):
  logger.info(reason)

  cmds = [
      f'''
      tmux set-hook -g {eventName} "run-shell 'tavs event {eventName}'"
      ''' for eventName in _events
  ]
  cmds = '\n'.join(cmds)
  _run(cmds)


def disable(reason):
  logger.info(reason)

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
