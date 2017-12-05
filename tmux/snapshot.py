#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import subprocess

import settings
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
    self.all_sessions = []  # list of tmux.Session objects

    #
    # scan live sessions
    #

    live_sessions = []
    w_width = 0  # max window name width
    s_width = 0  # max session name width

    p = subprocess.run(list_sessions_cmd, stdout=subprocess.PIPE)
    slines = p.stdout.decode().splitlines()

    for sline in slines:
      sid, sname = sline.split(':')
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])

      live_sessions.append(session)
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
    self.w_width = w_width
    self.s_width = s_width

    self.live_sessions = live_sessions
    self.all_sessions += live_sessions

    #
    # scan dead sessions
    #

    live_snames = [s.name for s in self.live_sessions]

    snames = [
        x.stem for x in settings.paths.sessions.glob('*')
        if not x.stem.startswith('.')]

    dead_snames = [n for n in snames if n not in live_snames]

    self.dead_sessions = []
    for idx, name in enumerate(dead_snames):
      session = tmux.Session(id=f'dead{idx}', name=name, loaded=False)

      self.dead_sessions.append(session)
      self.all_sessions.append(session)
