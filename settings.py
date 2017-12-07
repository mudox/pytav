#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path


class paths:
  install = Path(__file__).parent
  scripts = install / 'scripts'

  data = Path('~/.local/share/tav').expanduser()
  data.mkdir(parents=True, exist_ok=True)

  serve_dir = data / 'servers'
  serve_dir.mkdir(parents=True, exist_ok=True)

  fzf_feed = data / 'fzf-feed'
  width = data / 'fzf-width'
  sessions = data / 'sessions'
  hook_enabled = data_dir / 'update'


tav_session_name = 'Tav'
finder_window_name = 'Finder'
finder_window_target = f'{tav_session_name}:{finder_window_name}'


reenable_hook_interval = 4


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
