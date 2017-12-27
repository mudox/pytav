#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from textwrap import indent

from . import hook
from .. import settings as cfg
from .. import shell
from .agent import getSessionTTYSize

logger = logging.getLogger(__name__)


def isReady():
  out = shell.getStdout(f'''
      tmux list-panes -t {cfg.tmux.tavFrontWindowTarget} -F '#{{pane_current_command}}'
  ''')

  if out is None:
    return False, 'empty output'

  out = out.strip().splitlines()
  if len(out) != 1:
    return False, 'have more than 1 panes'

  if out[0] != 'Python':
    return False, f'invalid current pane command: {out}'

  return True, None


def create():

  if hook.isEnabled():
    hook.disable('before creating Tav session')
  else:
    logger.warning('hook is already disabled')

  sessionName = cfg.tmux.tavSessionName
  finderName = cfg.tmux.tavFrontWindowName
  finderTarget = cfg.tmux.tavFrontWindowTarget

  width, height = getSessionTTYSize()

  cmdstr = f"""
    # kill first for a clean creation
    tmux kill-session -t "{sessionName}" &>/dev/null

    set -ex

    # create session
    tmux new-session     \
      -s "{sessionName}" \
      -n "{finderName}"  \
      -x "{width}"       \
      -y "{height}"      \
      -d                 \
      sh

    tmux select-pane -t {finderTarget} -P bg="{cfg.colors.background}"

    # if it fails, the window is not affected
    # there may be some clue left
    tmux send-keys -t {finderTarget} 'tav interface' c-m

    # hide status bar, make it full screen like
    tmux set -t "{finderTarget}" status off

    sleep 1
  """
  shell.run(cmdstr)

  hook.enable('after creating Tav session')


def getFrontWindowTTY():
  output = shell.getStdout(
      f'tmux list-panes -t {cfg.tmux.tavFrontWindowTarget} -F "#{{pane_tty}}"'
  )

  if output is None:
    return None

  lines = output.strip().splitlines()
  if len(lines) != 1:
    logger.warning(f'expecting 1 line, got {len(lines)}:\n{indent(lines, "  ")}')
    if len(lines) == 0:
      return None

  return lines[0]


def getBackWindowTTY():
  output = shell.getStdout(
      f'tmux list-panes {cfg.tmux.tavBackWindowTarget} -F "#{{pane_tty}}"'
  )

  if output is None:
    return None

  lines = output.strip().splitlines()
  if len(lines) != 1:
    logger.warning(f'expecting 1 line, got {len(lines)}:\n{indent(lines, "  ")}')
    if len(lines) == 0:
      return None

  return lines[0]
