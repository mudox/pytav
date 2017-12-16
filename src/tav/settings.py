#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from . import tmux

tavSessionName = 'Tav'

finderWindowName = 'Finder'
finderWindowTarget = f'{tavSessionName}:{finderWindowName}'

logWindowTarget = f'{tavSessionName}:Log'

reenableHookInterval = 4

defaultConfig = {
    'version': 1,
    'color': {
        'live_session_name': '',
        'dead_session_name': '',
        'window_name': '',
        'dead_line': '',
        'background': '',
        'symbol': '',
    },
    'symbol': {
        'default': '+',
    }
}

serverPID = str(tmux.getServerPID())


class paths:

  # configuration
  configDir = Path('~/.config/tav').expanduser()
  configDir.mkdir(parents=True, exist_ok=True)

  config = configDir / 'settings.json'
  if not config.exists():
    # TODO!!: populate default json content to setting.json
    pass

  # install
  install = Path(__file__).parent
  scripts = install / 'scripts'

  # data
  dataDir = Path('~/.local/share/tav').expanduser()
  dataDir.mkdir(parents=True, exist_ok=True)

  # log
  logDir = dataDir / 'log'
  logDir.mkdir(parents=True, exist_ok=True)
  logFile = logDir / serverPID

  _tty = tmux.getLogTTY()
  logTTY = _tty is not None and Path(_tty) or None

  # serve file
  serveDir = dataDir / 'servers'
  serveDir.mkdir(parents=True, exist_ok=True)
  serveFile = serveDir / serverPID

  hookEnabled = dataDir / 'update'

  sessions = dataDir / 'sessions'


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
