#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import shlex
import shutil
import subprocess as sp
from os.path import getmtime
from textwrap import indent
from time import sleep

from . import settings as cfg
from . import screen, shell, tmux
from .fzf import FZFFormatter

logger = logging.getLogger(__name__)


# INFO: argument `event` is currently unused
def onTmuxEvent(event):
  # make sure the tav window is still there
  makeTavSession(force=False)

  # update interface data, if changed, refresh the UI
  dirty = update()
  if dirty:
    logger.debug('o:refresh tav window')
    tmux.refreshTavWindow()
  else:
    logger.debug('o: skip tav window refreshing')


def makeTavSession(force):
  if force:
    logger.info('forcedly recreate Tav session')
    tmux.tavSession.create()
  else:
    ready, msg = tmux.tavSession.isReady()
    if not ready:
      logger.warning(f'tav session not ready ({msg}), recreate it')
      tmux.tavSession.create()
    else:
      logger.info('tav session is ready, skip creation')


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
    mtime = getmtime(cfg.paths.userConfig)
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


def show(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  try:
    with cfg.paths.interfaceFile.open() as file:
      info = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError) as error:
    logger.warning('''
        error reading interface data from {cfg.paths.interfaceFile}:
        {indent(str(error), '  ')}
        update it first
        ''')
    update()
    with cfg.paths.interfaceFile.open() as file:
      info = json.load(file)

  #
  # window background
  #

  if not oneshot:
    shell.run(f'tmux select-pane -P bg={cfg.colors.background}')

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
      tmux.hook.enable(f'after creating dead session {tag}')
      tmux.showCursor(True)
