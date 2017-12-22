#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import fzf, settings, tmux


def test(args):
  settings.action = 'test'

  test_snapshot()
  test_formatter()
  # test_prepare_tmux_interface()


def _title(text):
  print(f'\n\033[35m{text}\033[0m\n')


def test_snapshot():
  _title('Test [snapshot] ...')
  snap = tmux.Snapshot()
  for s in snap.allSessions:
    print(f' {s.name:24} {s.loaded and "live" or "dead"}')

  print(f'\n windows: {snap.windowCount}')
  print(f' live sessions: {snap.liveSessionCount}')
  print(f' dead sessions: {snap.deadSessionCount}')
  print(f' server pid: {snap.serverPID}')


def test_formatter():
  _title('\nTest [formatter] ...')
  snap = tmux.Snapshot()
  formatter = fzf.FZFFormatter(snap, testMode=True)
  print(formatter.fzfFeed)


def test_prepare_tmux_interface():
  _title('\nTest [prepare tmux interface] ...')
  tmux.prepareTmuxInterface(force=False)
  tmux.prepareTmuxInterface(force=True)
