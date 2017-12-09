#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import tmux

tavSessionName = 'Tav'

finderWindowName = 'Finder'
finderWindowTarget = f'{tavSessionName}:{finderWindowName}'

logWindowTarget = f'{tavSessionName}:Log'

reenableHookInterval = 4


serverPID = str(tmux.getServerPID())

class paths:
  # installation
  install = Path(__file__).parent
  scripts = install / 'scripts'

  # data
  dataDir = Path('~/.local/share/tav').expanduser()
  dataDir.mkdir(parents=True, exist_ok=True)

  # log
  logDir = dataDir / 'log'
  logDir.mkdir(parents=True, exist_ok=True)
  logFile = logDir / serverPID

  logTTY = Path(tmux.getLogTTY())

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
