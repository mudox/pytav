#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from os.path import getmtime
from pathlib import Path
from textwrap import indent

from ruamel.yaml import YAML

from .screen import color2sgr, sgr

logger = logging.getLogger(__name__)


class _Section:
  pass


#
# sections
#

timestamp = None
paths = None
config = None
tmux = None
fzf = None
symbols = None
colors = None


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


def reload():
  # change the calling order with discretion
  _initPaths()

  _initConfig()
  _initTmux()
  _initFZF()

  _initColors()
  _initSymbols()


def _valueAt(*paths):
  u = _get(config.user, *paths)
  d = _get(config.default, *paths)
  return u, d


def _initPaths():
  global paths

  s = _Section()
  paths = s

  # install
  s.installDir = Path(__file__).parent
  s.scriptsDir = s.installDir / 'scripts'
  s.resourcesDir = s.installDir / 'resources'

  # config
  s.userConfigDir = Path('~/.config/tav').expanduser()
  s.userConfigDir.mkdir(parents=True, exist_ok=True)

  s.userConfig = s.userConfigDir / 'tav.yml'
  s.defaultConfig = s.resourcesDir / 'tav.yml'

  if not s.userConfig.exists():
    s.userConfig.write_text(s.defaultConfig.read_text())

  # data
  s.dataDir = Path('~/.local/share/tav').expanduser()
  s.dataDir.mkdir(parents=True, exist_ok=True)

  # sessions
  s.sessionsDir = s.dataDir / 'sessions'


def _initConfig():
  global config
  global timestamp

  s = _Section()
  config = s

  yaml = YAML()
  try:
    s.user = yaml.load(paths.userConfig)
  except BaseException as error:
    logger.error(f'''
      error reading user config file ({paths.userConfig}):
      {indent(str(error), '')}
      fill with default config content
    ''')
    text = paths.defaultConfig.read_text()
    paths.userConfig.write_text(text)
    s.user = yaml.load(paths.userConfig)

  timestamp = getmtime(paths.userConfig)
  s.default = yaml.load(paths.defaultConfig)


def _initTmux():
  global tmux

  s = _Section()
  tmux = s

  s.tavSessionName = 'Tav'

  s.tavFrontWindowName = 'Front'
  s.tavFrontWindowTarget = f'{s.tavSessionName}:{s.tavFrontWindowName}'

  s.tavBackWindowName = 'Back'
  s.tavBackWindowTarget = f'{s.tavSessionName}:{s.tavBackWindowName}'

  s.serverPID = _serverPID


def _initFZF():
  global fzf

  s = _Section()
  fzf = s

  # layoutLevel
  v, d = _valueAt('layoutLevel')
  if v in (0, 1, 2, 3, 4, 'auto'):
    s.layoutLevel = v
  else:
    s.layoutLevel = d
    logger.warning(f'invalid [layoutLevel] setting ({v}), fallback to `{d}`')

  s.topMargin = 3
  s.bottomMargin = 2
  s.hOffset = -3

  # minGap
  v, d = _valueAt('minGap')
  if isinstance(v, int) and v >= d:
    s.minGap = v
  else:
    s.minGap = d
    logger.warning(f'invalid [minGap] setting ({v}), fallback to `{d}`')

  # minWidth
  v, d = _valueAt('minWidth')
  if isinstance(v, int) and v >= d:
    s.minWidth = v
  else:
    s.minWidth = d
    logger.warning(f'invalid [minWidth] setting ({v}), fallback to `{d}`')


def _initSymbols():
  global symbols

  s = _Section()
  symbols = s

  # sessions dict
  use = _get(config.user, 'symbol.use')
  s.schemeName = use
  scheme = _get(config.user, 'symbol.schemes', use)

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
          f'ignore invalid sessoin symbol setting ({v}) for session name `{name}`')
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
  d = None
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


def _initColors():
  global colors

  s = _Section()
  colors = s

  use = _get(config.user, 'color.use')
  s.schemeName = use
  scheme = _get(config.user, 'color.schemes', use)
  defaultScheme = _get(config.default, 'color.schemes.default')

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


reload()
