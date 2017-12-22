#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path

from ruamel.yaml import YAML

from .screen import color2sgr, sgrHide
from .tmux.agent import getServerPID

logger = logging.getLogger(__name__)


#
# settings.tmux
#


class tmux:

  tavSessionName = 'Tav'

  finderWindowName = 'Finder'
  finderWindowTarget = f'{tavSessionName}:{finderWindowName}'

  logWindowTarget = f'{tavSessionName}:Log'

  maxDisableUpdateInterval = 10  # 10s

  serverPID = str(getServerPID())


#
# settings.paths
#

class paths:
  # installDir directory
  installDir = Path(__file__).parent
  scriptsDir = installDir / 'scripts'
  resourcesDir = installDir / 'resources'

  # configuration directory
  configDir = Path('~/.config/tav').expanduser()
  configDir.mkdir(parents=True, exist_ok=True)
  config = configDir / 'tav.yml'
  defaultConfig = resourcesDir / 'tav.yml'
  if not config.exists():
    config.write_text(defaultConfig.read_text())

  # data directory
  dataDir = Path('~/.local/share/tav').expanduser()
  dataDir.mkdir(parents=True, exist_ok=True)

  serveDir = dataDir / 'servers'
  serveDir.mkdir(parents=True, exist_ok=True)
  serveFile = serveDir / tmux.serverPID

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


class fzf:

  layoutLevel = _get(configData, 'layoutLevel') or 'auto'

  yMargin = 2

#
# settings.symbols
#


class symbols:

  _use = _get(configData, 'symbol.use')
  _scheme = _get(configData, 'symbol.schemes', _use)

  sessions = _get(_scheme, 'sessions')
  if not isinstance(sessions, dict):
    logger.warn('fail to load [symbols.sessions], fallback to default')
    sessions = {}

  unloaded = _get(_scheme, 'unloaded')
  if isinstance(unloaded, str) and unloaded.strip() != '':
    unloaded = unloaded[0]
  else:
    logger.warn('fail to load [symbols.unloaded], fallback to default')
    unloaded = '·'

  sessionDefault = _get(_scheme, 'sessionDefault')
  if isinstance(sessionDefault, str) and sessionDefault.strip() != '':
    sessionDefault = sessionDefault[0]
  else:
    logger.warn('fail to load [symbols.sessionDefault] fallback to default')
    sessionDefault = sgrHide('·')

#
# settings.colors
#


class colors:
  pass


_use = _get(configData, 'color.use')
_scheme = _get(configData, 'color.schemes', _use)
if not isinstance(_scheme, dict):
  logger.warn('fail to load [colors], fallback to all no color mode')
  _scheme = {}

_use = _get(defaultConfigData, 'color.use')
_default = _get(defaultConfigData, 'color.schemes', _use)

for name in _default:
  color = _scheme.get(name, 'white')
  color = color2sgr(color)
  setattr(colors, name, color)
