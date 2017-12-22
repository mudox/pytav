#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import shlex
import shutil
import subprocess
from time import sleep

from . import settings, tmux
from .fzf import FZFFormatter

logger = logging.getLogger(__name__)


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

  with settings.paths.serveFile.open('w') as file:
    json.dump(info, file)


def start_ui(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  if not settings.paths.serveFile.exists():
    logger.warn('server file ({settings.paths.serveFile}) does not exists, update first')
    update()

  with settings.paths.serveFile.open() as file:
    info = json.load(file)

  #
  # center fzf ui
  #

  t_width, t_height = shutil.get_terminal_size()
  width = info['fzf']['width']

  h_margin = int((t_width - width) / 2) - 3

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
    --margin={settings.fzf.yMargin},{h_margin}

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

  #
  # show fzf interface, get user selection
  #

  lines = info['fzf']['lines']

  process = subprocess.run(
      cmd,
      input=lines.encode(),
      stdout=subprocess.PIPE
  )

  if process.returncode != 0:
    # TODO!: alert error, wait for a key to continue
    return

  selectedLine = process.stdout.decode().strip()
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

      text = f'\033[33mCreating session [{tag}] ...\033[0m'
      tmux.showMessageCentered(text)

      #
      # create session
      #

      logger.info(f'load session [{tag}]')

      tmux.hook.disable()                        # disable hook updating

      path = settings.paths.sessions / tag           # create session
      subprocess.run(
          str(path),
          stdout=subprocess.DEVNULL
      )

      update()                                       # update snapshot

      sleep(1)                                       # warming

      tmux.switchTo(tag)

    finally:
      tmux.hook.enable()
      tmux.showCursor(True)
