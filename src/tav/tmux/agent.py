#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import shutil
from os import environ

from .. import settings as cfg
from .. import shell

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
    tmux select-pane -t ={cfg.tmux.tavWindowTarget} -P bg='{cfg.colors.background}'
    tmux send-keys -t ={cfg.tmux.tavWindowTarget} C-u C-t C-m
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
  lines = shell.getStdout(
      f'tmux list-sessions -F "#{{session_width}}x#{{session_height}}"'
  ).strip().splitlines()

  if lines is not None:
    w, h = lines[0].split('x')
    w, h = int(w), int(h)
  else:
    w, h = shutil.get_terminal_size()

  return w, h
