#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from textwrap import indent

from . import hook
from .. import settings as cfg
from .. import screen, shell
from .agent import getClientSize

logger = logging.getLogger(__name__)


def isReady():
  out = shell.getStdout(f'''
      tmux list-panes -t ={cfg.tmux.tavWindowTarget} -F '#{{pane_current_command}}'
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

  sname = cfg.tmux.tavSessionName

  wname = cfg.tmux.tavWindowName
  win = cfg.tmux.tavWindowTarget

  tmpsname = cfg.tmux.tavTmpSessionName
  tmpwin = cfg.tmux.tavTmpWindowTarget

  width, height = getClientSize()

  cmdstr = f"""
  if ! tmux has-session -t ={sname}; then
    tmux new-session        \
      -s '{sname}'          \
      -n '{wname}'          \
      -x '{width}'          \
      -y '{height}'         \
      -d                    \
      sh
    tmux select-pane -t {win} -P bg="{cfg.colors.background}"
    tmux send-keys -t {win} 'tav interface' c-m
    tmux set -t "{win}" status off
    exit
  fi

  if ! tmux has-session -t ={tmpsname}; then
    tmux new-session        \
      -s '{tmpsname}'       \
      -n '{wname}'          \
      -x '{width}'          \
      -y '{height}'         \
      -d                    \
      sh
  else
    tmux respawn-window -k -t '{tmpwin}' sh
  fi

  tmux select-pane -t {tmpwin} -P bg="{cfg.colors.background}"
  tmux send-keys -t {tmpwin} 'tav interface' c-m
  tmux set -t "{tmpwin}" status off

  sleep 1
  tmux swap-window -d -s '{win}' -t '{tmpwin}'
  """

  shell.run(cmdstr)

  # FIXME!!!: no use here
  showHeadLine('Tav (v3.1) by Mudox')

  hook.enable('after creating Tav session')


# ISSUE!!: no use
def showHeadLine(line):
  tty = getTavWindowTTY()
  if tty is None:
    return

  ttyWidth, _ = getClientSize()
  width = screen.screenWidth(line)
  x = (ttyWidth - width) / 2
  x = int(x) + cfg.fzf.hOffset

  cmdstr = f'''
  {{
    tput sc
    tput cup 1 1
    tput el
    tput cup 1 {x}
    echo "{line}"
    tput rc
  }} >> {tty}
  '''

  shell.run(cmdstr)


def getTavWindowTTY():
  ready, explain = isReady()
  if not ready:
    logger.warning(f'failed: {explain}')
    return None

  output = shell.getStdout(
      f'tmux list-panes -t {cfg.tmux.tavWindowTarget} -F "#{{pane_tty}}"'
  )

  if output is None:
    logger.error('o:failed')
    return None

  lines = output.strip().splitlines()
  if len(lines) != 1:
    logger.warning(f'expecting 1 line, got {len(lines)}:\n{indent(lines, "  ")}')
    if len(lines) == 0:
      return None

  return lines[0]
