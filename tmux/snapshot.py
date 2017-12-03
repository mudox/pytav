#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import shutil
import subprocess

import tmux


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
    result = {}
    w_width = 0  # max window name width
    s_width = 0  # max session name width

    p = subprocess.run(list_sessions_cmd, stdout=subprocess.PIPE)
    s_lines = p.stdout.decode().splitlines()

    for s_line in s_lines:
      sid, sname = s_line.split(':')
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      result[sid] = session

      s_width = max(s_width, len(sname))

      cmd = list_windows_cmd + [sid]
      p = subprocess.run(cmd, stdout=subprocess.PIPE)
      wlines = p.stdout.decode().splitlines()

      for wline in wlines:
        wid, wname = wline.split(':')
        window = tmux.Window(id=wid, name=wname)
        session.windows.append(window)

        w_width = max(w_width, len(wname))

    # widths
    t_width, t_height = shutil.get_terminal_size()

    self.w_width = w_width
    self.s_width = s_width
    self.session_map = result
