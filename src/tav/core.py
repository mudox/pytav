#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from . import settings as cfg
from . import tmux
from .fzf import FZFFormatter

logger = logging.getLogger(__name__)

model = None


# INFO: argument `event` is currently unused
def onTmuxEvent(event):
  model = updateModel()
  if model is not None:
    tmux.tavSession.create()


def updateModel():
  '''
  steps:
  - reload config.
  - regenerate the model data
  - compare with old model, return True if is dirty, else False
  - save model in `core.model`
  '''

  cfg.reload()

  snapshot = tmux.Snapshot()
  formatter = FZFFormatter(snapshot)

  newModel = {
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

  global model

  if newModel != model:
    logger.info('o:model is dirty')
    model = newModel
    return True
  else:
    logger.info('o:model is unchanged')
    return False
