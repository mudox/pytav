#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from . import core, settings, tests, tmux

__version__ = '2.2.2'

logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


class Command:

  def snapshot(self, args):
    settings.action = 'snapshot'

    core.update()

  def oneshot(self, args):
    settings.action = 'oneshot'

    core.update()
    core.start_ui(oneshot=True)

  def attach(self, args):
    settings.action = 'attach'

    core.update()
    tmux.switchTo(settings.tmux.finderWindowTarget)

  def serve(self, args):
    settings.action = 'serve'

    while True:
      core.start_ui(oneshot=False)

  def hook(self, args):
    settings.action = 'hook'

    if args.hookOption is None:  # perform hook update

      # must specify event type or arbitrary reason
      if args.event is None:
        msg = 'must specify either the trigger event type or [-d|-e] option\n\n'
        msg += self.parser.format_usage()
        print(msg)
        return

      settings.hookEvent = args.event

      tmux.prepareTmuxInterface(force=False)
      tmux.hook.run()

    else:

      if args.hookOption == 'enable':
        tmux.hook.enable()
      elif args.hookOption == 'disable':
        tmux.hook.disable()
      elif args.hookOption == 'print':
        line = 'hook: ' + ('enabled' if tmux.hook.isEnabled() else 'disabled')
        print(line)
      else:
        raise ValueError(f'Invalid argument parsing result, args.hookOption = `{args.hookOption}`')

  #
  # CLI interface
  #

  def __init__(self):

    self.parser = argparse.ArgumentParser(
        prog='tav',
        description='An tmux `choose-tree` replacement powered by fzf action.'
    )
    # defaults to update and choose once
    self.parser.set_defaults(func=self.oneshot)

    self.parser.add_argument(
        '--version',
        action='version',
        version=__version__
    )

    #
    # actions
    #

    subparsers = self.parser.add_subparsers(
        title='actions',
        description='without any action is equivalent to `oneshot`'
    )

    # action `snapshot`
    act_snapshot = subparsers.add_parser(
        'snapshot', aliases=['snp'],
        help='create a new snapshot tmux session window layout.'
    )
    act_snapshot.set_defaults(func=self.snapshot)

    # action `attach`
    act_attach = subparsers.add_parser(
        'attach', aliases=['a', 'at'],
        help='update backing data, and switch to Tav finder window'
    )
    act_attach.set_defaults(func=self.attach)

    # action `hook`
    act_hook = subparsers.add_parser(
        'hook', aliases=['h', 'hk', 'ho'],
        help='''
        update snapshot and update the fzf interface in tmux window
        '''
    )

    # hook {-d | -e | -p}
    group = act_hook.add_mutually_exclusive_group()
    group.add_argument(
        '-d, --disable',
        dest='hookOption',
        action='store_const',
        const='disable',
        help='disable background updating triggered by tmux hooks'
    )
    group.add_argument(
        '-e, --enable',
        dest='hookOption',
        action='store_const',
        const='enable',
        help='enable background updating'
    )
    group.add_argument(
        '-p, --print',
        dest='hookOption',
        action='store_const',
        const='print',
        help='enable background updating'
    )
    group.add_argument(
        'event',
        nargs='?',
        choices=[
            'window-linked',
            'window-renamed',
            'window-unlinked',
            'session-renamed',
            'after-enabled'
        ],
        help='event type that triggers the hook')
    act_hook.set_defaults(func=self.hook, hookOption=None)

    # action `oneshot`
    act_oneshot = subparsers.add_parser(
        'oneshot', aliases=['o', 'os'],
        help='''
        make a new snapshot and show the fzf interface, close after choose and
        switch. this is the DEFAULT action
        '''
    )
    act_oneshot.set_defaults(func=self.oneshot)

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
    act_serve.set_defaults(func=self.serve)

  def run(self):

    # dispatch tasks
    args = self.parser.parse_args()
    args.func(args)


def run():
  Command().run()
