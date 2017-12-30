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


def respawnYin():
  sname = cfg.tmux.yin.sname
  wname = cfg.tmux.yin.wname
  yin = cfg.tmux.yin.target
  width, height = agent.getClientSize()

  cmdstr = f"""
    tmux kill-session -t {sname}
    set -e
    tmux new-session        \
      -s '{sname}'          \
      -n '{wname}'          \
      -x '{width}'          \
      -y '{height}'         \
      -d                    \
      sh

    # set immediately after session recreation
    tmux set -w -t '{yin}' pane-base-index 0

    tmux select-pane -t {yin} -P bg="{cfg.colors.background}"
    tmux send-keys -t {yin} 'tav-core runloop' c-m
    tmux set -t "{yin}" status off
    sleep 0.7
  """

  shell.run(cmdstr)
  showHeadLine(yin, '─── Yin ───')
  disable(yin)


def respawnYang():
  sname = cfg.tmux.yang.sname
  wname = cfg.tmux.yang.wname
  yang = cfg.tmux.yang.target
  width, height = agent.getClientSize()

  cmdstr = f"""
    tmux kill-session -t {sname}
    set -e
    tmux new-session        \
      -s '{sname}'          \
      -n '{wname}'          \
      -x '{width}'          \
      -y '{height}'         \
      -d                    \
      sh

    # set immediately after session recreation
    tmux set -w -t '{yang}' pane-base-index 0

    tmux select-pane -t {yang} -P bg="{cfg.colors.background}"
    tmux send-keys -t {yang} 'tav-core runloop' c-m
    tmux set -t "{yang}" status off
    sleep 0.7
  """

  shell.run(cmdstr)

  if cfg.config.useDefautlConfig:
    showHeadLine(yang, 'USING DEFAULT CONFIG')
  else:
    showHeadLine(yang, '─── Yang ───')


def refreshYin():
  yin = cfg.tmux.yin.target

  enable(yin)

  shell.run(f'''
    tmux select-pane -t '{yin}' -P bg='{cfg.colors.background}'
    tmux send-keys -t '{yin}' C-u C-t C-m
    sleep 0.4
  ''')

  if cfg.config.useDefautlConfig:
    showHeadLine(yin, 'USING DEFAULT CONFIG')
  else:
    showHeadLine(yin, '─── Yang ───')




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
