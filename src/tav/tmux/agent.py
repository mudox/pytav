#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from shlex import split as xsplit
from os import environ

from . import hook, settings

logger = logging.getLogger(__name__)


def _run(cmdstr, *args):
  """Execute the command line using `subprocess.run`.

  The stdout & stderr are captured.

  Check the return code, log out stderr content if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell.
    args: other arguments will be passed to subprocess.run() as is.

  Returns:
    The process object returned from `subprocess.run`.
  """

  cmd = xsplit(cmdstr, comments=True)
  logger.debug(f'cmd: {cmd}')

  p = sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, *args)

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
  p = _run(cmdstr)
  return int(p.stdout.decode().strip().splitlines()[0])


def getLogTTY():
  cmdstr = f'''
    tmux list-panes -t {settings.logWindowTarget} -F '#{{pane_tty}}'
  '''

  p = _run(cmdstr)
  if p.returncode != 0:
    return None
  else:
    return p.stdout.decode().strip()


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

  p = _run(cmdstr)
  lines = p.stdout.decode().strip().splitlines()
  return [line.split(':') for line in lines]


def respawnFinderWindow():

  cmdstr = f'''
    tmux respawn-window -k -t '{settings.finderWindowTarget}'
  '''

  hook.enable(False)
  _run(cmdstr)
  hook.enable(True)


def switchTo(target):
  if 'TMUX' in environ:
    _run(f'tmux switch-client -t {target}')
  else:
    _run(f'tmux attach-session -t {target}')
