#!/usr/bin/env python3# -*- coding: utf-8 -*-

import logging
from textwrap import indent

from . import agent, hook
from .. import settings as cfg
from .. import screen, shell

logger = logging.getLogger(__name__)


def showHeadLine(target, line):
  tty = ttyOf(target)
  if tty is None:
    return

  ttyWidth, _ = agent.getClientSize()
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


def ttyOf(target):
  output = shell.getStdout(f'tmux list-panes -t {target} -F "#{{pane_tty}}"')

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


def isYinReady():
  # IDEA!!: use tmux.snapshot to do this

  out = shell.getStdout(f'''
      tmux list-panes -t {cfg.tmux.yin.target} -F '#{{pane_current_command}}'
  ''')

  # yin session and window must exist
  if out is None:
    return False, 'empty output, see error logging from `shell.getStdout`'

  # should have only one pane in the yin window
  out = out.strip().splitlines()
  if len(out) != 1:
    return False, 'have more than 1 panes in {cfg.tmux.yin.tmux}'

  # yin process must be running
  # FIXME!!!: the check logic is not solid, use unix domain socket instead
  if out[0] != 'Python':
    return False, f'invalid current pane command: {out}, expect `Python`'

  return True, None


def isYangReady():
  infoList = agent.dump()
  slice = [f'={i.sname}:={i.wname}' for i in infoList]
  count = slice.count(cfg.tmux.yang.target[:-2])
  if count == 0:
    return False, f'can not found yang session, or window'
  elif count > 1:
    return False, f'more than 1 pane in yang session'
  else:
    return True, None


def getYinReady(force):
  if force:
    logger.debug('o:force respawn yin')
    respawnYin()
  elif not isYinReady():
    logger.debug('o:yin is not ready, create it')
    respawnYin()
  else:
    logger.debug('o:skip')


def getYangReady(force):
  """
  Return: True if the yang window is recreated, hence no need to refresh or
  swap, its content is up to date, else return False.
  """
  if force:
    logger.debug('o:force respawn yang')
    respawnYang()
    return True
  elif not isYangReady():
    logger.debug('o:yang is not ready, create it')
    respawnYang()
    return True
  else:
    logger.debug('o:skip')
    return False



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
