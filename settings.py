#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import subprocess
from pathlib import Path


class paths:
  install = Path(__file__)
  scripts = install / 'scripts'

  data = Path('~/.local/share/tav').expanduser()

  fzf_feed = data / 'fzf-feed'
  width = data / 'fzf-width'
  update = data / 'update'
  sessions = data / 'sessions'


nav_window_target = 'Tmux:Navigator'
log_window_target = 'Tmux:Log'


def log_tty():
  cmd = [
      'tmux', 'list-panes',
      '-t', log_window_target,
      '-F', '"#{pane_tty}"',
  ]
  return subprocess.getoutput(
      f'tmux list-panes -t "{log_window_target}"' + ' -F "#{pane_tty}"')


paths.data.mkdir(parents=True, exist_ok=True)

reenable_hook_interval = 4


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
