#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import shlex
import shutil
import subprocess
from time import sleep

import settings
import tmux
from fzf_feeder import FZFFormatter


def prepare_tmux_interface(force):
  '''
  check states of tav tmux session and windows
  create if not available
  '''
  cmd = settings.paths.scripts / 'prepare-tmux-interface.sh'
  subprocess.call([str(cmd), force and 'kill' or 'nokill'])


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
  fzf_feed_lines = formatter.fzf_lines()
  fzf_ui_width = formatter.fzf_width

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

  serve_feed = settings.paths.serve_dir / str(snap.server_pid)
  with serve_feed.open('w') as file:
    json.dump(info, file)


def start_ui(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  t_width, t_height = shutil.get_terminal_size()
  width = int(settings.paths.width.read_text())

  h_margin = int((t_width - width) / 2) - 3
  t_margin = 3

  cmd = shlex.split(f'''
    fzf
    --exact

    # hide prefixing tag's
    --with-nth=2..

    # retain the relationship between matched sessions and windows
    --tiebreak=index

    # disable all quit bindings

    --ansi
    --height=100%

    # center interface in the terminal screen
    --margin={t_margin},{h_margin}

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

  with settings.paths.fzf_feed.open() as file:

    #
    # show fzf interface, get user selection
    #

    process = subprocess.run(
        cmd,
        stdin=file,
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
      subprocess.run(['tmux', 'switch-client', '-t', tag])

    # other auxiliary lines, e.g. dead sessions group line
    elif tag == '<nop>':
      return

    # dead session line
    else:
      try:

        #
        # show creating message
        #

        subprocess.run('clear')                        # clear screen
        subprocess.run(f'tput civis'.split())          # hide cursor
        x = int(t_width / 2 - 12)
        y = int(t_height / 2)
        subprocess.run(f'tput cup {y} {x}'.split())    # center message

        print(f'\033[33mCreating session [{tag}] ...\033[0m', end=None)

        #
        # create session
        #

        tmux.hook.enable(False)                        # disable hook updating

        path = settings.paths.sessions / tag           # create session
        subprocess.run(
            str(path),
            stdout=subprocess.DEVNULL
        )

        update()                                       # update snapshot

        sleep(1)                                       # warming

        subprocess.call(['tmux', 'switch-client', '-t', tag])

      finally:
        tmux.hook.enable(True)
        subprocess.run(['tput', 'cnorm'])
