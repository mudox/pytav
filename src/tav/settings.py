#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path

from ruamel.yaml import YAML

from . import tmux
from .screen import sgrHide

logger = logging.getLogger(__name__)

tavSessionName = 'Tav'

finderWindowName = 'Finder'
finderWindowTarget = f'{tavSessionName}:{finderWindowName}'

logWindowTarget = f'{tavSessionName}:Log'

maxDisableUpdateInterval = 10  # 10s

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
  scriptsDir = install / 'scripts'
  resourcesDir = install / 'resources'

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
  logFile = logDir / 'log'

  _tty = tmux.getLogTTY()
  logTTY = _tty is not None and Path(_tty) or None

  # serve file
  serveDir = dataDir / 'servers'
  serveDir.mkdir(parents=True, exist_ok=True)
  serveFile = serveDir / serverPID

  update = dataDir / 'update'

  sessions = dataDir / 'sessions'


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
