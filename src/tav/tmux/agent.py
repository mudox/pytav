#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import shutil
from os import environ
from typing import NamedTuple

from .. import shell

logger = logging.getLogger(__name__)


class dumpInfo(NamedTuple):
  # session
  sid: str
  sname: str

  # window
  wid: str
  wname: str
  windex: int
  wwidth: int
  wheight: int

  # pane
  ptty: str


def dump():
  '''
  Return generator for dumpInfo (named tuple) sequence.
  '''

  # yapf: disable
  format = [
      # session
      '#{session_id}',
      '#{session_name}',
      # windwo
      '#{window_id}',
      '#{window_name}',
      '#{window_index}',
      '#{window_width}',
      '#{window_height}',
      # pane
      '#{pane_tty}',
  ]
  # yapf: enable

  format = ':'.join(format)

  cmdstr = f'''
    tmux list-windows -a -F '{format}'
  '''

  out = shell.getStdout(cmdstr)
  lines = out.strip().splitlines()

  infoList = []
  for line in lines:
    t = line.split(':')

    sid,         \
        sname,   \
        wid,     \
        wname,   \
        windex,  \
        wwidth,  \
        wheight, \
        ptty = t

    info = dumpInfo(
        # session
        sid=sid,
        sname=sname,
        # window
        wid=wid,
        wname=wname,
        windex=windex,
        wwidth=wwidth,
        wheight=wheight,
        # pane
        ptty=ptty,
    )

    infoList.append(info)

  return infoList


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
      f'tmux list-sessions -F "#{{session_width}}x#{{session_height}}"')

  if lines is None:
    return shutil.get_terminal_size()

  lines = lines.strip().splitlines()

  if len(lines) > 0:
    w, h = lines[0].split('x')
    w, h = int(w), int(h)
  else:
    w, h = shutil.get_terminal_size()

  return w, h


def getCurrentSession():
  out = shell.getStdout("""
    tmux list-clients -F '#{client_session}'
  """)

  if out is None:
    return None

  lines = out.strip().splitlines()
  if len(lines) == 0:
    return None
  else:
    return lines[0]
