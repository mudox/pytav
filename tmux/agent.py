#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess as sp
from shlex import split


def list_all_windows():
  '''
  return tuple of (sid, sname, wid, wname)
  '''

  format = '#{session_id}:#{session_name}:#{window_id}:#{window_name}'

  cmd = split(f'''
    tmux list-windows -a -F '{format}'
  ''', comments=True)

  p = sp.run(cmd, stdout=sp.PIPE)
  lines = p.stdout.decode().splitlines()
  return [line.split(':') for line in lines]
