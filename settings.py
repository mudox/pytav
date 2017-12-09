#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import tmux

tav_session_name = 'Tav'
finder_window_name = 'Finder'
finder_window_target = f'{tav_session_name}:{finder_window_name}'

reenable_hook_interval = 4


class paths:
  # installation
  install = Path(__file__).parent
  scripts = install / 'scripts'

  # data
  data_dir = Path('~/.local/share/tav').expanduser()
  data_dir.mkdir(parents=True, exist_ok=True)
  # log
  logDir = dataDir / 'log'
  logDir.mkdir(parents=True, exist_ok=True)
  logFile = logDir / serverPID

  logTTY = Path(tmux.getLogTTY())

  serve_dir = data_dir / 'servers'
  serve_dir.mkdir(parents=True, exist_ok=True)
  serve_file = serve_dir / str(tmux.get_server_pid())

  hook_enabled = data_dir / 'update'
  sessions = data_dir / 'sessions'


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
