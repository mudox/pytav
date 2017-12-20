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
  # install
  install = Path(__file__).parent
  scriptsDir = install / 'scripts'
  resourcesDir = install / 'resources'

  # configuration
  configDir = Path('~/.config/tav').expanduser()
  configDir.mkdir(parents=True, exist_ok=True)
  config = configDir / 'tav.yml'
  defaultConfig = resourcesDir / 'tav.yml'
  if not config.exists():
    config.write_text(defaultConfig.read_text())

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


# config data
_yaml = YAML()
configData = _yaml.load(paths.config)
defaultConfigData = _yaml.load(paths.defaultConfig)


def _get(d, *keyss):
  if d is None:
    return None

  if keyss is None:
    return None

  for keys in keyss:
    if keys is None:
      return None

    keys = keys.split('.')
    for key in keys:
      d = d.get(key, None)
      if d is None:
        return None

  return d


class symbols:

  _schemeName = _get(configData, 'symbols.use')
  _scheme = _get(configData, 'symbols', _schemeName)

  sessionSymbols = _get(_scheme, 'session')
  if not isinstance(sessionSymbols, dict):
    logger.warn('fail to load [symbols.sessionSymbols] fallback to default')
    sessionSymbols = {}

  unloaded = _get(_scheme, 'unloaded')
  if isinstance(unloaded, str) and unloaded.strip() != '':
    unloaded = unloaded[0]
  else:
    logger.warn('fail to load [symbols.unloaded] fallback to default')
    unloaded = '·'

  sessionDefault = _get(_scheme, 'sessionDefault')
  if isinstance(sessionDefault, str) and sessionDefault.strip() != '':
    sessionDefault = sessionDefault[0]
  else:
    logger.warn('fail to load [symbols.sessionDefault] fallback to default')
    sessionDefault = sgrHide('·')
