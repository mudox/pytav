#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import shutil
import subprocess
from pathlib import Path

from snapshot import TmuxSnapshot

out_dir = Path('~/.local/share/tav').expanduser()
out_dir.mkdir(parents=True, exist_ok=True)
fzf_feed_path = out_dir / 'fzf-feed'
width_path = out_dir / 'width'
update_path = out_dir / 'update'


def update():
  '''
  take a new snapshot and write to data files.
  '''

  snapshot = TmuxSnapshot()

  with open(str(fzf_feed_path), 'w') as file:
    file.write(snapshot.fzf_lines())

  with open(str(width_path), 'w') as file:
    file.write(str(snapshot.width))


def choose_tree(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  t_width, t_height = shutil.get_terminal_size()
  with open(width_path) as file:
    width = int(file.read())

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
      cmd.append(f'--bind={key}:execute(tmux switch-client -p)')

    # prevent ctrl-z suspend fzf
    cmd.append('--bind=ctrl-z:unix-line-discard')

  with open(str(fzf_feed_path)) as file:
    process = subprocess.run(cmd, stdin=file, stdout=subprocess.PIPE)
    if process.returncode != 0:
      return

    result = process.stdout.decode().split()
    if len(result) == 0:  # may select an empty line
      return

    target_id = result[0]
    subprocess.run(['tmux', 'switch-client', '-t', target_id])
