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
    slines = p.stdout.decode().splitlines()

    for sline in slines:
      sid, sname = sline.split(':')
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      result[sid] = session

      s_width = max(s_width, len(sname))

      cmd = list_windows_cmd + [sid]
      p = subprocess.run(cmd, stdout=subprocess.PIPE)
      wlines = p.stdout.decode().splitlines()

      for wline in wlines:
        wid, wname = wline.split(':')

        # filter out all Tav window
        if sname == 'Tmux' and wname == 'Navigator':
          continue

        window = tmux.Window(id=wid, name=wname)
        session.windows.append(window)

        w_width = max(w_width, len(wname))

      if len(session.windows) == 0:
        assert session.name == 'Tmux'
        del result[session.id]

    # widths
    t_width, t_height = shutil.get_terminal_size()

    self.w_width = w_width
    self.s_width = s_width
    self.session_map = result
