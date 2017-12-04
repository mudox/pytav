#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import shutil
import subprocess
from formatter import FZFFormatter

import settings
import tmux


def create_tmux_interface(force):
  cmd = settings.paths.scripts / 'tav.tmux-session.sh'
  subprocess.run([str(cmd), force and 'kill' or 'nokill'])


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

    id = process.stdout.decode().split('\t')[0].strip()
    if len(id) == 0:  # may select an empty line
      return

    if id.startswith('$') or id.startswith('@'):
      subprocess.run(['tmux', 'switch-client', '-t', id])
    elif len(id.strip()) > 0:
      try:
        # interface transition
        subprocess.run('clear')
        x = int(t_width / 2 - 10)
        y = int(t_height / 2)
        subprocess.run(f'tput cup {y} {x}'.split())
        subprocess.run(f'tput civis'.split())
        print(f'\033[33mCreating session [{id}] ...\033[0m', end=None)

        path = settings.paths.sessions / id
        subprocess.run(
            str(path),
            stdout=subprocess.DEVNULL,
            stderr=open(settings.log_tty(), 'w')
        )

      finally:
        subprocess.run(['tput', 'cnorm'])
