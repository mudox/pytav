# -*- coding: utf-8 -*-

from . import fzf, tmux


def dump(args, targets=None):
  if len(targets) == 0:
    _config()
    _snapshot()
    _formatter()
  elif 'config' in targets:
    _config()
  elif 'snapshot' in targets:
    _snapshot()
  elif 'formatter' in targets:
    _formatter()


def _title(text):
  print(f'\n\033[35m{text}\033[0m\n')


def _snapshot():
  _title('\n[snapshot] ...')
  snap = tmux.Snapshot()
  for s in snap.allSessions:
    print(f' {s.name:24} {s.loaded and "live" or "dead"}')

  print(f'\n windows: {snap.windowCount}')
  print(f' live sessions: {snap.liveSessionCount}')
  print(f' dead sessions: {snap.deadSessionCount}')
  print(f' server pid: {snap.serverPID}')


def _formatter():
  _title('\n[formatter] ...')
  snap = tmux.Snapshot()
  formatter = fzf.FZFFormatter(snap, testMode=True)
  print(formatter.fzfFeed)


def _config():
  _title('\n[config] ...')
  # TODO!: dump config content
