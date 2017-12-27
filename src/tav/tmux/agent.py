#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import shutil
from functools import reduce
from os import environ
from shutil import get_terminal_size

from .. import settings as cfg
from .. import shell
from ..screen import screenWidth

logger = logging.getLogger(__name__)


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

  out = shell.getStdout(cmdstr)
  lines = out.strip().splitlines()
  return [line.split(':') for line in lines]


def refreshTavWindow():
  shell.run(f'''
    tmux select-pane -t {cfg.tmux.tavWindowTarget} -P bg='{cfg.colors.background}'
    tmux send-keys -t {cfg.tmux.tavWindowTarget} C-u C-t C-m
  ''')


def switchTo(target):
  # quote for sessions id e.g. '$5'
  # avoid shell parsing on it
  target = f"'{target}'"

  if 'TMUX' in environ:
    p = shell.run(f'tmux switch-client -t {target}')
  else:
    p = shell.run(f'tmux attach-session -t {target}')

  return p


def getClientSize():
  # FIXME!!!: handle mutiple command situation
  if 'TMUX' in environ and len(environ['TMUX']) > 0:
    lines = shell.getStdout(
        f'tmux list-clients -F "#{{client_width}}x#{{client_height}}"'
    ).strip().splitlines()
    w, h = lines[0].split('x')
  else:
    # outside of tmux
    w, h = shutil.get_terminal_size()

  return w, h
