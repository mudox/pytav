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
      tmux list-panes -t ={cfg.tmux.tavFrontWindowTarget} -F '#{{pane_current_command}}'
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

  fname = cfg.tmux.tavFrontWindowName
  front = cfg.tmux.tavFrontWindowTarget

  bname = cfg.tmux.tavFrontWindowName
  back = cfg.tmux.tavFrontWindowTarget

  back = f'{sname}:$'

  width, height = getClientSize()

  cmdstr = f"""
  if ! tmux has-session -t ={sname}; then
    tmux new-session        \
      -s '{sname}'          \
      -n '{fname}'          \
      -x '{width}'          \
      -y '{height}'         \
      -d                    \
      sh

    tmux select-pane -t {front} -P bg="{cfg.colors.background}"
    tmux send-keys -t {front} 'tav interface' c-m
    tmux set -t "{front}" status off

    sleep 1
    exit
  fi

  tmux respawn-window -k -t '{back}' sh
  if [[ $? -ne 0 ]]; then
    tmux new-window              \
      -a                         \
      -t '{sname}:{{end}}'       \
      -n '{bname}'               \
      -d                         \
      sh
  fi

  tmux select-pane -t {back} -P bg="{cfg.colors.background}"
  tmux send-keys -t {back} 'tav interface' c-m
  tmux set -t "{back}" status off

  sleep 1
  tmux swap-window -d -s '{front}' -t '{back}'
  tmux rename-window -t '{sname}:^' {fname}
  tmux rename-window -t '{sname}:$' {bname}
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
      f'tmux list-panes -t {cfg.tmux.tavFrontWindowTarget} -F "#{{pane_tty}}"'
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
