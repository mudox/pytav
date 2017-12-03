#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os
import shlex
import subprocess
from pathlib import Path

import hook
from core import choose_tree, update

out_dir = Path('~/.local/share/tav').expanduser()
out_dir.mkdir(parents=True, exist_ok=True)
fzf_feed_path = out_dir / 'fzf-feed'
width_path = out_dir / 'width'
update_path = out_dir / 'update'


def snapshot(args):
  update()


def oneshot(args):
  update()
  choose_tree(oneshot=True)


def serve(args):
  while True:
    choose_tree(oneshot=False)


def hook_command(args):
  create_navigator_window_if_neede()

  if args.hook_enabled is None:
    hook.run()
  else:
    hook.enable(args.hook_enabled)


def create_navigator_window_if_neede():

  process = subprocess.run(
      ['tmux', 'list-panes', '-t', 'Tmux:Navigator'],
      stdout=subprocess.DEVNULL
  )

  if process.returncode != 0:
    # get client tty size
    p = subprocess.run(shlex.split('''
      tmux list-clients -F '#{client_width}:#{client_height}'
    ''', stdout=subprocess.PIPE))

    if p.returncode != 0:
      raise RuntimeError('`tmux list-clients` failed')

    width, height = map(int, p.stdout.decode().split(':'))

    # get script path
    script_path = os.path.dirname(os.path.abspath(__file__))
    cmd = f'{script_path}/tav.py serve'

    p = subprocess.run(shlex.split(f'''
      tmux new-session
      -s Tmux -n Navigator
      -x {width} -y {height}
      -d
      {cmd}
    '''))


def parse_args():
  parser = argparse.ArgumentParser(
      prog='tav',
      description='An tmux `choose-tree` replacement powered by fzf command.'
  )
  parser.set_defaults(func=oneshot)  # defaults to update and choose once
  subparsers = parser.add_subparsers(
      title='actions',
      description='without any action is equivalent to `oneshot`'
  )

  # command `update`
  act_snapshot = subparsers.add_parser(
      'snapshot', aliases=['snp'],
      help='create a new snapshot tmux session window layout.'
  )
  act_snapshot.set_defaults(func=snapshot)

  # command `hook`
  act_hook = subparsers.add_parser(
      'hook', aliases=['h', 'hk', 'ho'],
      help='update snapshot and update the fzf interface in tmux window `Tmux:Navigator`.'
  )
  group = act_hook.add_mutually_exclusive_group()
  group.add_argument(
      '-d, --disable',
      dest='hook_enabled',
      action='store_false',
      help='disable background updating triggered by tmux hooks'
  )
  group.add_argument(
      '-e, --enable',
      dest='hook_enabled',
      action='store_true',
      help='enable background updating'
  )
  act_hook.set_defaults(func=hook_command, hook_enabled=None)

  # command `oneshot`
  act_oneshot = subparsers.add_parser(
      'oneshot', aliases=['o', 'os'],
      help='make a new snapshot and show the fzf interface, close after choose and switch. this is the DEFAULT action'
  )
  act_oneshot.set_defaults(func=oneshot)

  # command `serve`
  act_serve = subparsers.add_parser(
      'serve', aliases=['srv'],
      help='show the fzf inteface, remain after choose and switch.'
  )
  act_serve.set_defaults(func=serve)

  # options = parser.parse_args()
  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  parse_args()
