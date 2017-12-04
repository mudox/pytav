#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import core
import fzf_feeder
import settings
import tmux


def test(args):
  settings.action = 'test'
  test_settings()
  test_snapshot()
  test_formatter()
  test_prepare_tmux_interface()


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
  formatter = fzf_feeder.FZFFormatter(snap)
  print(formatter.fzf_lines())


def test_prepare_tmux_interface():
  _title('\nTest [prepare tmux interface] ...')
  core.prepare_tmux_interface(force=False)
  core.prepare_tmux_interface(force=True)
