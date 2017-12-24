#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import fzf, tmux


def diagnose(args):
  _snapshot()
  _formatter()


def _title(text):
  print(f'\n\033[35m{text}\033[0m\n')


def _snapshot():
  _title('Test [snapshot] ...')
  snap = tmux.Snapshot()
  for s in snap.allSessions:
    print(f' {s.name:24} {s.loaded and "live" or "dead"}')

  print(f'\n windows: {snap.windowCount}')
  print(f' live sessions: {snap.liveSessionCount}')
  print(f' dead sessions: {snap.deadSessionCount}')
  print(f' server pid: {snap.serverPID}')


def _formatter():
  _title('\nTest [formatter] ...')
  snap = tmux.Snapshot()
  formatter = fzf.FZFFormatter(snap, testMode=True)
  print(formatter.fzfFeed)


def _prepare_tmux_interface():
  _title('\nTest [prepare tmux interface] ...')
  tmux.prepareTmuxInterface(force=False)
  tmux.prepareTmuxInterface(force=True)
