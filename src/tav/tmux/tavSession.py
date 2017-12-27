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
  windowName = cfg.tmux.tavWindowName

  tmpSessionName = '_' * 8 + sessionName
  tmpWindowTarget = f'{tmpSessionName}:{windowName}'

  width, height = getClientSize()

  cmdstr = f"""
    # kill first for a clean creation
    tmux kill-session -t "{tmpSessionName}" &>/dev/null

    # create session
    tmux new-session        \
      -s "{tmpSessionName}" \
      -n "{windowName}"     \
      -x "{width}"          \
      -y "{height}"         \
      -d                    \
      sh

    tmux select-pane -t {tmpWindowTarget} -P bg="{cfg.colors.background}"

    # if it fails, the window is not affected
    # there may be some clue left
    tmux send-keys -t {tmpWindowTarget} 'tav interface' c-m

    # hide status bar, make it full screen like
    tmux set -t "{tmpWindowTarget}" status off

    sleep 1

    # start moving
    # tmux switch-client -t {tmpWindowTarget}
    tmux kill-session -t '{sessionName}'
    tmux rename-session -t '{tmpSessionName}' '{sessionName}'
  """
  shell.run(cmdstr)

  showHeadLine('Tav (v3.1) by Mudox')

  hook.enable('after creating Tav session')


# ISSUE!!: no use
def showHeadLine(line):
  tty = getTavWindowTTY()
  if tty is None:
    return

  w, _ = getClientSize()
  logger.debug(f'w: {w}')
  w0 = screen.screenWidth(line)
  logger.debug(f'w0: {w0}')
  x = (w - w0) / 2
  logger.debug(f'x: {x}')
  x = int(x) + cfg.fzf.hOffset
  logger.debug(f'x: {x}')

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
