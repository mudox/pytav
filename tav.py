#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import shlex
import shutil
import subprocess
from pathlib import Path

from snapshot import TmuxSnapshot

out_dir = Path('~/.local/share/tmux-choose-tree').expanduser()
out_dir.mkdir(parents=True, exist_ok=True)
feed_path = out_dir / 'fzf-feed'
width_path = out_dir / 'width'
update_path = out_dir / 'update'


def update():
  snapshot = TmuxSnapshot()

  with open(str(feed_path), 'w') as file:
    file.write(snapshot.fzf_lines())

  with open(str(width_path), 'w') as file:
    file.write(str(snapshot.width))

def choose(once):
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

  if not once:
    cmd.append('--no-clear')
    for key in ('esc', 'ctrl-c', 'ctrl-g', 'ctrl-q'):
      cmd.append(f'--bind={key}:execute(tmux switch-client -p)')

  with open(str(feed_path)) as file:
    process = subprocess.run(cmd, stdin=file, stdout=subprocess.PIPE)
    if process.returncode != 0:
      return

    result = process.stdout.decode().split()
    if len(result) == 0:  # may select an empty line
      return

    target_id = result[0]
    subprocess.run(['tmux', 'switch-client', '-t', target_id])


def hook_update():
  if not is_hook_update_enabled():
    return
  else:
    update()
    subprocess.run(['tmux', 'respawn-window', '-k', '-t', 'Tmux:Navigator'])


def is_hook_update_enabled():
  if not update_path.exists():
    return True

  with open(str(update_path)) as file:
    if file.read() == 'no':
      return False
    else:
      return True


def set_hook_update(enable):
  with open(str(update_path), 'w') as file:
    file.write(enable and 'yes' or 'no')


def main():
  cliParser = argparse.ArgumentParser(
      prog='tav',
      description='An tmux choose-tree alternative powered by fzf'
  )
  cliParser.add_argument(
      'action',
      nargs='?',
      default='update and choose once',
      help='one of update|once|interface'
  )
  options = cliParser.parse_args()

  if options.action == 'update':
    update()
  elif options.action == 'once':
    choose(once=True)
  elif options.action == 'hook':
    hook_update()
  elif options.action == 'interface':
    while True:
      choose(once=False)
  elif options.action == 'update and choose once':
    update()
    choose(once=True)
  else:
    cliParser.print_help()


if __name__ == "__main__":
  main()
