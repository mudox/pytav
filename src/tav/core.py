#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from textwrap import indent

from . import settings as cfg
from . import tmux
from .fzf import FZFFormatter

logger = logging.getLogger(__name__)


# INFO: argument `event` is currently unused
def onTmuxEvent(event):
  dirty = update()
  if dirty:
    tmux.tavSession.create()


def update():
  '''
  steps:
  - reload config if user config file is modified since last load
  - take a new snapshot
  - tansform (format) the snapshot into interface model
  - compare with old model, dump and return True is is different, else return
    False
  '''

  #
  # user config
  #

  global cfg

  try:
    mtime = cfg.paths.userConfig.stat().st_mtime
    if mtime != cfg.timestamp:
      logger.info(f'config file ({cfg.paths.userConfig}) is changed, reload')
      cfg.reload()
  except BaseException as error:
    logger.warning(f'''
        error getting mtime of user config from {cfg.paths.userConfig}:
        {indent(str(error), '  ')}
        reload the config
    ''')
    cfg.reload()

  #
  # snapshot
  #

  snapshot = tmux.Snapshot()
  formatter = FZFFormatter(snapshot)

  info = {
      'tmux': {
          'serverPID': snapshot.serverPID,
          'windowCount': snapshot.windowCount,
          'liveSessionCount': snapshot.liveSessionCount,
          'deadSessionCount': snapshot.deadSessionCount,
      },
      'fzf': {
          'width': formatter.fzfWidth,
          'header': formatter.fzfHeader,
          'lines': formatter.fzfFeed,
          'backgroundColor': cfg.colors.background,
      }
  }

  try:
    with cfg.paths.interfaceFile.open() as file:
      oldInfo = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError) as error:
    logger.warning(f'''
        error reading interface data from {cfg.paths.interfaceFile}:
        {indent(str(error), '  ')}
    ''')
    with cfg.paths.interfaceFile.open('w') as file:
      json.dump(info, file)
    return True

  if info != oldInfo:
    logger.info('o:interface model data is dirty')
    with cfg.paths.interfaceFile.open('w') as file:
      json.dump(info, file)
    return True
  else:
    logger.info('o:interface model data is not changed')
    return False
