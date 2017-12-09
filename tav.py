#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

import core
import log
import settings
import tests
import tmux

log.configureLogging()
logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


def snapshot(args):
  settings.action = 'snapshot'

  core.update()


def oneshot(args):
  settings.action = 'oneshot'

  core.update()
  core.start_ui(oneshot=True)


def serve(args):
  settings.action = 'serve'

  while True:
    core.start_ui(oneshot=False)


def hook(args):
  settings.action = 'hook'

  if args.hookEnabled is None:
    tmux.prepareTmuxInterface(force=False)
    tmux.hook.run()
  else:
    tmux.hook.enable(args.hookEnabled)

#
# CLI interface
#


def parse_args():
  parser = argparse.ArgumentParser(
      prog='tav',
      description='An tmux `choose-tree` replacement powered by fzf action.'
  )
  parser.set_defaults(func=oneshot)  # defaults to update and choose once

  parser.add_argument('--version', action='version', version='1.1')
  parser.add_argument(
      '-v, --verbose',
      action='store_true',
      dest='verbose',
      help='verbose (debug) mode'
  )

  #
  # actions
  #

  subparsers = parser.add_subparsers(
      title='actions',
      description='without any action is equivalent to `oneshot`'
  )

  # action `snapshot`
  act_snapshot = subparsers.add_parser(
      'snapshot', aliases=['snp'],
      help='create a new snapshot tmux session window layout.'
  )
  act_snapshot.set_defaults(func=snapshot)

  # action `hook`
  act_hook = subparsers.add_parser(
      'hook', aliases=['h', 'hk', 'ho'],
      help='''
      update snapshot and update the fzf interface in tmux window
      '''
  )
  group = act_hook.add_mutually_exclusive_group()
  group.add_argument(
      '-d, --disable',
      dest='hookEnabled',
      action='store_false',
      help='disable background updating triggered by tmux hooks'
  )
  group.add_argument(
      '-e, --enable',
      dest='hookEnabled',
      action='store_true',
      help='enable background updating'
  )
  act_hook.set_defaults(func=hook, hookEnabled=None)

  # action `oneshot`
  act_oneshot = subparsers.add_parser(
      'oneshot', aliases=['o', 'os'],
      help='''
      make a new snapshot and show the fzf interface, close after choose and
      switch. this is the DEFAULT action
      '''
  )
  act_oneshot.set_defaults(func=oneshot)

  # action: `test`
  act_oneshot = subparsers.add_parser(
      'test', aliases=['t', 'te'],
  )
  act_oneshot.set_defaults(func=tests.test)

  # action `serve`
  act_serve = subparsers.add_parser(
      'serve', aliases=['srv'],
      help='show the fzf inteface, remain after choose and switch.'
  )
  act_serve.set_defaults(func=serve)

  # dispatch tasks
  args = parser.parse_args()

  settings.verbose = args.verbose
  args.func(args)


if __name__ == "__main__":
  parse_args()
