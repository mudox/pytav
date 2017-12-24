#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import shutil
import subprocess as sp
from functools import reduce
from os import environ
from shutil import get_terminal_size

from ..screen import screenWidth
from ..settings import cfg

logger = logging.getLogger(__name__)


def _check(cmdstr):
  return _run(cmdstr).returncode == 0


def _system(cmdstr):
  # left unchanged (connect to controlling terminal)
  _run(cmdstr, stdoutArg=None)


def _getStdout(cmdstr):
  p = _run(cmdstr, stdoutArg=sp.PIPE)
  return p.returncode == 0 and p.stdout.decode() or None


def _run(cmdstr, stdoutArg=sp.DEVNULL, trace=True):
  """Execute the command line using `subprocess.run`.

  The stdout's redirection is controlled by the argument `stdoutArg`, which is
    `DEVNULL` by defaults.
  The stderr is captured.

  Check the return code, log out content captured from stderr if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell which can contain
      comments.
    stdoutArg (number of file object): Control the redireciton of the stdout.

  Returns:
    The process object returned from `subprocess.run`.
  """

  # logger.debug(f'cmd: {cmdstr.strip()}')
  cmdstr = f'set -x\n{cmdstr}'

  p = sp.run(cmdstr, shell=True, stderr=sp.PIPE, stdout=stdoutArg)

  text = p.stderr.decode()
  if p.returncode != 0:
    logger.error(f'fail to execute:\n{text}\nerror code: {p.returncode})')
  else:
    logger.debug(f'succeed to execute:\n{text}')

  return p


def prepareTmuxInterface(force):
  """
  Check the availability of tav tmux session and windows, create them if not.
  """

  cmd = cfg.paths.scriptsDir / 'prepare-tmux-interface.sh'
  sp.call([str(cmd), force and 'kill' or 'nokill'])


def getServerPID():
  cmdstr = '''
    tmux list-sessions -F '#{pid}'
  '''
  out = _getStdout(cmdstr)
  if out is not None:
    return int(out.strip().splitlines()[0])
  else:
    return None


def getLogTTY():
  cmdstr = f'''
    tmux list-panes -t {cfg.tmux.logWindowTarget} -F '#{{pane_tty}}'
  '''

  out = _getStdout(cmdstr)
  if out is not None:
    return out.strip()
  else:
    return None


def dumpInfo():
  '''
  return tuples about tmux snapshot
  '''

  format = [
      '#{session_id}',       # 0
      '#{session_name}',     # 1

      '#{window_id}',        # 2
      '#{window_name}',      # 3
      '#{window_index}',     # 4
      '#{window_width}',     # 5
      '#{window_height}',    # 6
  ]
  format = ':'.join(format)

  cmdstr = f'''
    tmux list-windows -a -F '{format}'
  '''

  out = _getStdout(cmdstr)
  lines = out.strip().splitlines()
  return [line.split(':') for line in lines]


def refreshFinderWindow():
  cmdstr = f'''
    tmux send-keys -t {cfg.tmux.finderWindowTarget} C-u C-t C-m
  '''

  _run(cmdstr)


def switchTo(target):
  # quote for sessions id e.g. '$5'
  # avoid shell parsing on it
  target = f"'{target}'"

  if 'TMUX' in environ:
    p = _run(f'tmux switch-client -t {target}')
  else:
    p = _run(f'tmux attach-session -t {target}')

  return p


def showMessageCentered(text):
  # clear screen & hide cursor
  _system('clear; tput civis')

  ttyWidth, ttyHeight = get_terminal_size()

  lines = text.splitlines()
  textHeight = len(lines)
  textWidth = reduce(max, [screenWidth(line) for line in lines])

  x = int((ttyWidth - textWidth) / 2)
  y = int((ttyHeight - textHeight) / 2)

  _system(f'tput cup {y} {x}')

  print(text, end=None)


def showCursor(flag):
  if flag:
    _system('tput cnorm')
  else:
    _system('tput civis')


def getSessionTTYSize():
  if 'TMUX' in environ and len(environ['TMUX']) > 0:
    # inside of tmux
    w = _getStdout(
        r'tmux list-clients -t . -F "#{client_width}"'
    ).splitlines()[0]
    h = _getStdout(
        r'tmux list-clients -t . -F "#{client_height}"'
    ).splitlines()[0]
  else:
    # outside of tmux
    w, h = shutil.get_terminal_size()

  return w, h


def isTavSessionReady():
  finderReady = _check(f'tmux list-panes -t {cfg.tmux.finderWindowTarget}')
  if not finderReady:
    logger.warning('finder window is not ready')

  logReady = _check(f'tmux list-panes -t {cfg.tmux.logWindowTarget}')
  if not logReady:
    logger.warning('log window is not realdy')

  return finderReady and logReady


def createTavSession():
  # TODO!!: disable hook update

  sessionName = cfg.tmux.tavSessionName
  finderName = cfg.tmux.finderWindowName
  finderTarget = cfg.tmux.finderWindowTarget
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
