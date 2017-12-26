#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from pathlib import Path

from ruamel.yaml import YAML

from .screen import color2sgr, sgrHide

logger = logging.getLogger(__name__)


cmdstr = '''
  tmux list-sessions -F '#{pid}'
'''
p = sp.run(cmdstr, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
if p.returncode == 0:
  _serverPID = p.stdout.decode().strip().splitlines()[0]
else:
  raise RuntimeError('no tmux server')


def _get(d, *paths):
  """ Query into configuration dictionary, return None on any error
  usag:
    _get(d, 'k1.2.k3.k4', 2, 'name')
  """
  if d is None:
    return None

  if paths is None:
    return None

  for path in paths:
    if path is None:
      return None

    path = path.split('.')
    for key in path:
      try:
        i = int(key)
        if i in d:
          return d[i]
        else:
          return None

      except BaseException:
        d = d.get(key, None)
        if d is None:
          return None

  return d


class _Section:
  pass


class _Settings:

  def __init__(self):
    self._initPaths()
    self._initCongfig()
    self._initTmux()
    self._initFZF()
    self._initSymbols()
    self._initColors()

  def _valueAt(self, *paths):
    u = _get(self.userConfig, *paths)
    d = _get(self.defaultConfig, *paths)
    return u, d

  def _initPaths(self):

    s = _Section()
    self.paths = s

    # installDir directory
    s.installDir = Path(__file__).parent
    s.scriptsDir = s.installDir / 'scripts'
    s.resourcesDir = s.installDir / 'resources'

    # configuration directory
    s.userConfigDir = Path('~/.config/tav').expanduser()
    s.userConfigDir.mkdir(parents=True, exist_ok=True)

    s.userConfig = s.userConfigDir / 'tav.yml'
    s.defaultConfig = s.resourcesDir / 'tav.yml'

    if not s.userConfig.exists():
      s.userConfig.write_text(s.defaultConfig.read_text())

    # data directory
    s.dataDir = Path('~/.local/share/tav').expanduser()
    s.dataDir.mkdir(parents=True, exist_ok=True)

    s.interfaceDir = s.dataDir / 'interface'
    s.interfaceDir.mkdir(parents=True, exist_ok=True)
    s.interfaceFile = s.interfaceDir / _serverPID

    s.sessionsDir = s.dataDir / 'sessions'

  def _initCongfig(self):
    yaml = YAML()
    self.userConfig = yaml.load(self.paths.userConfig)
    self.userConfigMTime = getmtime(self.paths.userConfig)
    self.defaultConfig = yaml.load(self.paths.defaultConfig)

  def _initTmux(self):
    s = _Section()
    self.tmux = s

    s.tavSessionName = 'Tav'
    s.tavWindowName = 'Finder'
    s.tavWindowTarget = f'{s.tavSessionName}:{s.tavWindowName}'

    s.serverPID = _serverPID

  def _initFZF(self):
    s = _Section()
    self.fzf = s

    # layoutLevel
    v, d = self._valueAt('layoutLevel')
    if v in (0, 1, 2, 3, 4, 'auto'):
      s.layoutLevel = v
    else:
      s.layoutLevel = d
      logger.warning(f'invalid [layoutLevel] setting ({v}), fallback to `{d}`')

    # yMargin
    v, d = self._valueAt('yMargin')
    if isinstance(v, int) and v > 0:
      s.yMargin = v
    else:
      s.yMargin = d
      logger.warning(f'invalid [yMargin] setting ({v}), fallback to `{d}`')

    # minGap
    v, d = self._valueAt('minGap')
    if isinstance(v, int) and v >= d:
      s.minGap = v
    else:
      s.minGap = d
      logger.warning(f'invalid [minGap] setting ({v}), fallback to `{d}`')

    # minWidth
    v, d = self._valueAt('minWidth')
    if isinstance(v, int) and v >= d:
      s.minWidth = v
    else:
      s.minWidth = d
      logger.warning(f'invalid [minWidth] setting ({v}), fallback to `{d}`')

  def _initSymbols(self):
    s = _Section()
    self.symbols = s

    # sessions dict
    use = _get(self.userConfig, 'symbol.use')
    scheme = _get(self.userConfig, 'symbol.schemes', use)

    v = _get(scheme, 'sessions')
    if isinstance(v, dict):
      s.sessions = v
    else:
      logger.warning(
          f'invalid [symbols.sessions] settings ({v}), fallback to empty dict')
      s.sessions = {}

    invalidNames = []
    for name in s.sessions:
      v = s.sessions[name]
      if isinstance(v, str):
        s.sessions[name] = v[0]
      else:
        logger.warning(
            f'ignore invalid sessoin symbol setting ({c}) for session name `{name}`')
        invalidNames.append(name)

    for name in invalidNames:
      del s.sessions[name]

    # unloaded
    v = _get(scheme, 'unloaded')
    d = '·'
    if isinstance(v, str) and v.strip() != '':
      s.unloaded = v[0]
    else:
      logger.warning(
          f'invalid [symbols.unloaded] setting ({v}), fallback to default')
      s.unloaded = d

    # sessionDefault
    v = _get(scheme, 'sessionDefault')
    d = sgrHide('·')
    if isinstance(v, str) and v.strip() != '':
      s.sessionDefault = v[0]
    else:
      logger.warning(
          f'invalid [symbols.sessionDefault] setting ({v}), fallback to default')
      s.sessionDefault = d

    # windowDefault
    v = _get(scheme, 'windowDefault')
    d = '·'
    if isinstance(v, str) and v.strip() != '':
      s.windowDefault = v[0]
    else:
      logger.warning(
          f'invalid [symbols.windowDefault] setting ({v}), fallback to default')
      s.windowDefault = d

  def _initColors(self):
    s = _Section()
    self.colors = s

    use = _get(self.userConfig, 'color.use')
    scheme = _get(self.userConfig, 'color.schemes', use)
    defaultScheme = _get(self.defaultConfig, 'color.schemes.default')

    if not isinstance(scheme, dict):
      logger.info(
          f'invalid [colors] type ({type(scheme)}), fall back to default scheme')
      scheme = defaultScheme

    for name in defaultScheme:
      color = scheme.get(name, 'white')

      code = color2sgr(color)
      if code is None:
        color = 'white'

      if name == 'background':
        setattr(s, name, color)
      else:
        setattr(s, name, code)


cfg = _Settings()
