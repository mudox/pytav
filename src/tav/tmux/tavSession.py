#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging

from . import hook
from ..settings import cfg
from .agent import _getStdout, _run, getSessionTTYSize

logger = logging.getLogger(__name__)


def isReady():
  out = _getStdout(f'''
      tmux list-panes -t {cfg.tmux.tavWindowTarget} -F '#{{pane_current_command}}'
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
  finderName = cfg.tmux.tavWindowName
  finderTarget = cfg.tmux.tavWindowTarget

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

    # if it fails, the window is not affected
    # there may be some clue left
    tmux send-keys -t {finderTarget} 'tav interface' c-m
    # hide status bar, make it full screen like
    tmux set -t "{finderTarget}" status off

    sleep 1
  """
  _run(cmdstr)

  hook.enable('after creating Tav session')
