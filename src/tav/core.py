#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import shlex
import shutil
import subprocess as sp
from time import sleep

from . import screen, tmux
from .fzf import FZFFormatter
from .settings import cfg

logger = logging.getLogger(__name__)

def startServer():
  # TODO!!!: start server instance
  pass

def makeTavSession(force=False):
  if force:
    logger.info('forcedly recreate Tav session')
    tmux.tavSession.create()
  else:
    ready, msg = tmux.tavSession.isReady()
    if not ready:
      logger.warning('tav session not ready ({msg}), recreate it')
      tmux.tavSession.create()
    else:
      logger.info('tav session is ready, skip creation')


def update():
  '''
  steps:
  - take a new snapshot
  - tansform (format) the snapshot info into fzf feed lines
  - wrap all info into a dict
  - `json.dump` the dict to disk
  '''

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
      }
  }

  with cfg.paths.serveFile.open('w') as file:
    json.dump(info, file)


def show(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  if not cfg.paths.serveFile.exists():
    logger.warn(
        'serve file ({cfg.paths.serveFile}) does not exists, update first')
    update()

  with cfg.paths.serveFile.open() as file:
    info = json.load(file)

  # window background
  cmdstr = f"""
    tmux select-pane -P bg={cfg.colors.background}
  """
  p = sp.run(cmdstr, shell=True, stdout=sp.DEVNULL, stderr=sp.PIPE)
  if p.returncode != 0:
    logger.error(f'error setting finder window background color:\n{p.stderr.decode()}')

  #
  # center fzf ui
  #

  tWidth, _ = shutil.get_terminal_size()
  width = info['fzf']['width']

  hMargin = int((tWidth - width) / 2) - 3

  #
  # compose fzf command line
  #

  cmd = shlex.split(f'''
    fzf
    --exact

    # hide prefixing tag's
    --with-nth=2..

    # retain the relationship between matched sessions and windows
    --tiebreak=index

    --ansi          # color mode
    --height=100%   # fullscreen mode

    # center interface in the terminal screen
    --margin={cfg.fzf.yMargin},{hMargin}

    --header='{info["fzf"]["header"]}'
    --inline-info

    # fully transparent background
    --color=bg:-1,bg+:-1
  ''', comments=True)

  if not oneshot:
    # avoid screen flickering
    cmd.append('--no-clear')

    # prevent keys to abort fzf
    for key in ('esc', 'ctrl-c', 'ctrl-g', 'ctrl-q'):
      cmd.append(f'--bind={key}:unix-line-discard+execute(tmux switch-client -l)')

    # prevent ctrl-z suspend fzf
    cmd.append('--bind=ctrl-z:unix-line-discard')

    cmd.append('--bind=ctrl-t:top')

  #
  # show fzf interface, get user selection
  #

  lines = info['fzf']['lines']

  p = sp.run(
      cmd,
      input=lines.encode(),
      stdout=sp.PIPE
  )

  if p.returncode != 0:
    logger.error('fzf command failed')
    return

  selectedLine = p.stdout.decode().strip()
  tag = selectedLine.split('\t')[0].strip()

  #
  # handle the tag
  #

  # empty separate line
  if len(tag) == 0:
    return

  # live session or window line
  elif tag.startswith('$') or tag.startswith('@'):
    p = tmux.switchTo(tag)
    if p.returncode != -0:
      tmux.showMessageCentered('Switching failed, update data ...')
      update()
    return

  # other auxiliary lines, e.g. dead sessions group line
  elif tag == '<nop>':
    return

  # handle dead session line
  # TODO!!: split actions into methods
  else:
    try:

      #
      # show creating message
      #

      color = cfg.colors.message
      text = f'Creating session [{tag}] ...'
      text = screen.sgr(text, color)
      tmux.showMessageCentered(text)

      #
      # create session
      #

      logger.info(f'load session [{tag}]')
      tmux.hook.disable(f'before creating dead session {tag}')

      path = cfg.paths.sessionsDir / tag
      p = sp.run(
          str(path),
          stdout=sp.DEVNULL,
          stderr=sp.PIPE
      )

      if p.returncode != 0:
        logger.error(f'fail to create session [{tag}]: {p.stderr.decode()}')
        color = cfg.colors.error
        text = f'Creating session [{tag}] FAILED!'
        text = screen.sgr(text, color)
        tmux.showMessageCentered(text)
        update()
        sleep(1)
        return
      else:
        update()
        sleep(1)
        tmux.switchTo(tag)

    finally:
      tmux.hook.enable()
      tmux.showCursor(True)
