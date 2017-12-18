#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from os import environ
from shlex import split as xsplit
from shutil import get_terminal_size
from functools import reduce

from .. import settings
from . import hook
from ..screen import screenWidth

logger = logging.getLogger(__name__)


def _system(cmdstr):
  """Execute the command line using `subprocess.run`.

  The stdout is left unchanged (link to controlling tty).
  The stderr is captured.

  Check the return code, log out content captured from stderr if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell which can contain comments.
  """

  _run(cmdstr, stdoutArg=None)


def _getStdout(cmdstr):
  """Execute the command line using `subprocess.run`.

  The stdout is captured
  The stderr is captured.

  Check the return code, log out content captured from stderr if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell which can contain comments.

  Returns:
    The captured stdout content if run successfully, `None` otherwise.
  """

  p = _run(cmdstr, stdoutArg=sp.PIPE)

  return p.returncode == 0 and p.stdout.decode() or None


def _run(cmdstr, stdoutArg=sp.DEVNULL):
  """Execute the command line using `subprocess.run`.

  The stdout is redirected to /dev/null.
  The stderr is captured.

  Check the return code, log out content captured from stderr if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell which can contain comments.

  Returns:
    The process object returned from `subprocess.run`.
  """

  logger.debug(f'cmd string: {cmdstr}')

  cmd = xsplit(cmdstr, comments=True)
  logger.debug(f'splitted: {cmd}')

  p = sp.run(cmdstr, shell=True, stderr=sp.PIPE, stdout=stdoutArg)

  if p.returncode != 0:
    msg = p.stderr.decode()
    logger.error(f'error: {msg}')

  return p


def prepareTmuxInterface(force):
  """
  Check the availability of tav tmux session and windows, create them if not.
  """

  cmd = settings.paths.scripts / 'prepare-tmux-interface.sh'
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
    tmux list-panes -t {settings.logWindowTarget} -F '#{{pane_tty}}'
  '''

  out = _getStdout(cmdstr)
  if out is not None:
    return out.strip()
  else:
    return None


def listAllWindows():
  '''
  return tuple of (sid, sname, wid, wname)
  '''

  format = [
      '#{session_id}',
      '#{session_name}',
      '#{window_id}',
      '#{window_name}',
  ]
  format = ':'.join(format)

  cmdstr = f'''
    tmux list-windows -a -F '{format}'
  '''

  out = _getStdout(cmdstr)
  lines = out.strip().splitlines()
  return [line.split(':') for line in lines]


def respawnFinderWindow():

  cmdstr = f'''
    tmux respawn-window -k -t '{settings.finderWindowTarget}'
  '''

  hook.enable(False)
  _run(cmdstr)
  hook.enable(True)


def switchTo(target):
  # quote for sessions id e.g. '$5'
  # otherwise it would be expanded as an shell variable
  target = f"'{target}'"

  if 'TMUX' in environ:
    _run(f'tmux switch-client -t {target}')
  else:
    _run(f'tmux attach-session -t {target}')


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
