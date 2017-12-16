#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from shlex import split as xsplit

from . import settings
from . import hook

logger = logging.getLogger(__name__)


def prepareTmuxInterface(force):
  '''
  check states of tav tmux session and windows
  create if not
  '''
  cmd = settings.paths.scripts / 'prepare-tmux-interface.sh'
  sp.call([str(cmd), force and 'kill' or 'nokill'])


def getServerPID():
  cmd = split('''
    tmux list-sessions -F '#{pid}'
  ''')
  p = sp.run(cmd, stdout=sp.PIPE)

  return int(p.stdout.decode().strip().splitlines()[0])


def getLogTTY():
  cmd = split(f'''
    tmux list-panes -t {settings.logWindowTarget} -F '#{{pane_tty}}'
  ''')

  p = sp.run(cmd, stdout=sp.PIPE)
  if p.returncode != 0:
    return None
  else:
    return p.stdout.decode().strip()


def list_all_windows():
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

  cmd = split(f'''
    tmux list-windows -a -F '{format}'
  ''', comments=True)

  p = sp.run(cmd, stdout=sp.PIPE)
  lines = p.stdout.decode().strip().splitlines()
  return [line.split(':') for line in lines]


def respawn_finder_window():

  cmd = f'''
    tmux respawn-window -k -t '{settings.finderWindowTarget}'
  '''

  hook.enable(False)
  execute(cmd)
  hook.enable(True)


def execute(cmdstr, *args):
  cmd = xsplit(cmdstr, comments=True)
  logger.debug(f'cmd: {cmd}')

  p = sp.run(cmd, stderr=sp.PIPE, stdout=sp.PIPE, *args)

  if p.returncode != 0:
    msg = p.stderr.decode()
    logger.error(f'error: {msg}')

  return p
