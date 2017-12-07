#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
from shlex import split

def get_server_pid() -> int:
  cmd = split('''
    tmux list-clients -F '#{pid}'
  ''')
  p = sp.run(cmd, stdout=sp.PIPE)

  return int(p.stdout.decode().strip().splitlines()[0])

def list_all_windows() -> list:
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