#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from ..settings import cfg
from .agent import _getStdout, _run, getSessionTTYSize


def isReady():
  out = _getStdout(f'''
      tmux list-panes -t {cfg.tmux.tavWindowTarget} -F {{ane_current_command}}
  ''')

  if out is None:
    return False, 'empty output'

  out = out.strip().splitlines()
  if len(out) != 1:
    return False, 'have more than 1 panes'

  if out != 'Python':
    return False, f'invalid current pane command: {out}'

  return True, None


def create():
  # TODO!!: disable hook update

  sessionName = cfg.tmux.tavSessionName
  finderName = cfg.tmux.tavWindowName
  finderTarget = cfg.tmux.tavWindowTarget
  logName = cfg.tmux.logWindowName
  logTarget = cfg.tmux.logWindowTarget

  width, height = getSessionTTYSize()

  cmdstr = f"""
    set -uo pipefail

    # kill first for a clean creation
    tmux kill-session -t "{sessionName}" &>/dev/null

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
    tmux send-keys -t {finderTarget} tav serve c-m

    # hide status bar, make it full screen like
    tmux set -t "{finderTarget}" status off

    # log window
    tmux new-window              \
      -a                         \
      -t "{sessionName}:{{end}}" \
      -n "{logName}"             \
      -d                         \
      sh

    # black it out
    tmux send-keys -t "{logTarget}" '
    tput civis
    stty -echo
    PS1=
    '

    # disable the window
    tmux select-pane -t "{logTarget}.1" -d
  """

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
    tmux send-keys -t {finderTarget} 'tav serve' c-m

    # hide status bar, make it full screen like
    tmux set -t "{finderTarget}" status off

    # log window
    tmux new-window              \
      -a                         \
      -t "{sessionName}:{{end}}" \
      -n "{logName}"             \
      -d                         \
      sh

    # black it out
    tmux send-keys -t "{logTarget}" '
    tput civis
    stty -echo
    PS1=
    '

    # disable the window
    tmux select-pane -t "{logTarget}.1" -d
  """
  _run(cmdstr)
