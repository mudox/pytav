#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fzf_feeder import FZFFormatter
import settings

import tmux


def test(args):
  settings.action = 'test'
  test_settings()
  # test_snapshot()
  test_formatter()

def _title(text):
  print(f'\n\033[35m{text}\033[0m\n')

def test_settings():
  _title('Test [settings] ...')
  tty = settings.log_tty()
  print(f'log window tty: {tty}')

def test_snapshot():
  _title('Test [snapshot] ...')
  snap = tmux.Snapshot()
  for s in snap.all_sessions:
    print(f' {s.name:24} {s.loaded and "live" or "dead"}')


def test_formatter():
  _title('\nTest [formatter] ...')
  snap = tmux.Snapshot()
  formatter = FZFFormatter(snap)
  print(formatter.fzf_lines())
