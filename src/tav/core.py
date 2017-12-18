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

  snap = tmux.Snapshot()

  formatter = FZFFormatter(snap)
  fzf_feed_lines = formatter.fzfLines()
  fzf_ui_width = formatter.width

  logger.debug(f'fzf ui width: {fzf_ui_width}')
  logger.debug(fzf_feed_lines)

  info = {
      'tmux': {
          'server_pid': snap.server_pid,
          'window_count': snap.window_count,
          'live_session_count': snap.live_session_count,
          'dead_session_count': snap.dead_session_count,
      },
      'fzf': {
          'ui_width': fzf_ui_width,
          'lines': fzf_feed_lines,
      }
  }

  with settings.paths.serveFile.open('w') as file:
    json.dump(info, file)


def start_ui(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  with settings.paths.serveFile.open() as file:
    info = json.load(file)

  # fzf header string
  header = '{} sessions ({} alive, {} dead), {} windows'.format(
      info['tmux']['live_session_count'] + info['tmux']['dead_session_count'],
      info['tmux']['live_session_count'],
      info['tmux']['dead_session_count'],
      info['tmux']['window_count'],
  )

  # center fzf ui
  t_width, t_height = shutil.get_terminal_size()
  width = info['fzf']['ui_width']

  h_margin = int((t_width - width) / 2) - 3
  t_margin = 3

  # compose fzf command line
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
    --margin={t_margin},{h_margin}

    --header='{header}'
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

  tag = process.stdout.decode().split('\t')[0].strip()

  #
  # handle the tag
  #

  # empty separate line
  if len(tag) == 0:
    return

  # live session or window line
  elif tag.startswith('$') or tag.startswith('@'):
    tmux.switchTo(tag)

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

      tmux.hook.enable(False)                        # disable hook updating

      path = settings.paths.sessions / tag           # create session
      subprocess.run(
          str(path),
          stdout=subprocess.DEVNULL
      )

      update()                                       # update snapshot

      sleep(1)                                       # warming

      tmux.switchTo(tag)

    finally:
      tmux.hook.enable(True)
      tmux.showCursor(True)
