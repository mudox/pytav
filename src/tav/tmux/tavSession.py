#!/usr/bin/env python3# -*- coding: utf-8 -*-

import logging
from textwrap import indent

from . import agent, hook
from .. import settings as cfg
from .. import screen, shell

logger = logging.getLogger(__name__)





  else:




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
    tmux send-keys -t {win} 'tav-core interface' c-m
    tmux set -t "{win}" status off
    exit
  else
    tmux select-pane -t {win} -d
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
  tmux send-keys -t {tmpwin} 'tav-core interface' c-m
  tmux set -t "{tmpwin}" status off

  sleep 0.8
  tmux swap-window -d -s '{win}' -t '{tmpwin}'
  tmux select-pane -t {tmpwin} -e
  """

  shell.run(cmdstr)

  if cfg.config.useDefautlConfig:
    showHeadLine(f'USING DEFAULT CONFIG')
  else:
    showHeadLine(f'─── Tav ───')

  hook.enable('after creating Tav session')


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
    tput civis
    tput sc
    tput cup 1 1
    tput el
    tput cup 1 {x}
    echo "{line}"
    tput rc
    tput cnorm
  }} >> {tty}
  '''

  shell.run(cmdstr)



  output = shell.getStdout(
      f'tmux list-panes -t {cfg.tmux.tavWindowTarget} -F "#{{pane_tty}}"')

  if output is None:
    logger.error('o:failed')
    return None

  lines = output.strip().splitlines()
  if len(lines) != 1:
    logger.warning(
        f'expecting 1 line, got {len(lines)}:\n{indent(lines, "  ")}')
    if len(lines) == 0:
      return None

  return lines[0]


def enable(target):
  shell.run(f"""
    tmux select-pane -t '{target}' -e
  """)


def disable(target):
  shell.run(f"""
    tmux select-pane -t '{target}' -d
  """)
