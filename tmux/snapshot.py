#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import shutil
import subprocess

from model import Session, Window


list_sessions_cmd = shlex.split('''
  tmux
  list-sessions
  -F
  '#{session_id}:#{session_name}'
''', comments=True)

list_windows_cmd = shlex.split('''
  tmux
  list-windows
  -F
  '#{window_id}:#{window_name}'
  -t
''', comments=True)


class Snapshot:

  def __init__(self):
    '''
      take a snapshot
    '''
    snapshot = {}
    w_width = 0  # max window name width
    s_width = 0  # max session name width

    p = subprocess.run(list_sessions_cmd, stdout=subprocess.PIPE)
    s_lines = p.stdout.decode().splitlines()

    for s_line in s_lines:
      s_id, s_name = s_line.split(':')
      session = Session(id=s_id, name=s_name, loaded=True, windows=[])
      snapshot[s_id] = session

      s_width = max(s_width, len(s_name))

      cmd = list_windows_cmd + [s_id]
      p = subprocess.run(cmd, stdout=subprocess.PIPE)
      w_lines = p.stdout.decode().splitlines()

      for w_line in w_lines:
        w_id, w_name = w_line.split(':')
        window = Window(id=w_id, name=w_name)
        session.windows.append(window)

        w_width = max(w_width, len(w_name))

    # widths
    t_width, t_height = shutil.get_terminal_size()

    self.s_width = s_width
    self.w_width = w_width

    prefix_width = 4
    self.gap = 10

    self.width = prefix_width + w_width + s_width + self.gap
    self.snapshot = snapshot
