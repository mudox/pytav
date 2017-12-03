#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import shutil
import subprocess
from formatter import FZFFormatter

import settings
import tmux


def update():
  '''
  take a new snapshot and write to data files.
  '''

  formatter = FZFFormatter(tmux.Snapshot())
  settings.paths.fzf_feed.write_text(formatter.fzf_lines())
  settings.paths.width.write_text(str(formatter.fzf_ui_width))


def choose_tree(oneshot):
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

    # hide prefixing id's
    --with-nth=2..

    # retain the relationship between matched sessions and windows
    --tiebreak=index

    # disable all quit bindings

    --ansi
    --height=100%

    # center interface in the terminal screen
    --margin={t_margin},{h_margin}

    # fully transparent background
    --color=bg:-1,bg+:-1
  ''', comments=True)

  if not oneshot:
    # avoid screen flickering
    cmd.append('--no-clear')

    # prevent keys to abort fzf
    for key in ('esc', 'ctrl-c', 'ctrl-g', 'ctrl-q'):
      cmd.append(f'--bind={key}:execute(tmux switch-client -l)')

    # prevent ctrl-z suspend fzf
    cmd.append('--bind=ctrl-z:unix-line-discard')

  with settings.paths.fzf_feed.open() as file:
    process = subprocess.run(cmd, stdin=file, stdout=subprocess.PIPE)
    if process.returncode != 0:
      return

    result = process.stdout.decode().split()
    if len(result) == 0:  # may select an empty line
      return

    target_id = result[0]
    subprocess.run(['tmux', 'switch-client', '-t', target_id])
