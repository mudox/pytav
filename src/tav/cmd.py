#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from contextlib import suppress

from . import core, tmux, ui
from .diagnose import diagnose
from .server import start as startServer

__version__ = '2.3'

logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


class Command:

  def actionOneshot(self, args):
    ui.show(oneshot=True)

  def actionServer(self, args):
    with suppress(KeyboardInterrupt):
      startServer(port=32323)

  def actionInterface(self, args):
    while True:
      ui.show(oneshot=False)

  def actionHook(self, args):
    if args.hookOption is None:  # perform hook update
      core.onTmuxEvent(args.event)

    else:

      if args.hookOption == 'enable':
        tmux.hook.enable('invoked from command')
      elif args.hookOption == 'disable':
        tmux.hook.disable('invoked from command')
      elif args.hookOption == 'print':
        line = 'hook: ' + ('enabled' if tmux.hook.isEnabled() else 'disabled')
        print(line)

  #
  # CLI interface
  #

  def __init__(self):

    self.parser = argparse.ArgumentParser(
        prog='tav',
        description='An tmux `choose-tree` replacement powered by fzf action.'
    )
    # defaults to update and choose once
    self.parser.set_defaults(func=self.actionOneshot)

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

    #
    # action `hook`
    #

    act_hook = subparsers.add_parser(
        'hook', aliases=['h', 'hk', 'ho'],
        help='''
        update snapshot and update the fzf interface in tmux window
        '''
    )
    act_hook.set_defaults(func=self.actionHook, hookOption=None)

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
        help='event type that triggers the hook')

    #
    # action `oneshot`
    #

    act_oneshot = subparsers.add_parser(
        'oneshot',
        help='''
        make a new snapshot and show the fzf interface, close after choose and
        switch. this is the DEFAULT action
        '''
    )
    act_oneshot.set_defaults(func=self.actionOneshot)

    #
    # action: `diagnose`
    #

    act_oneshot = subparsers.add_parser(
        'diagnose', aliases=['d', 'dia'],
        help='dump diagnose infomation'
    )
    act_oneshot.set_defaults(func=diagnose)

    #
    # action `server`
    #

    act_server = subparsers.add_parser(
        'server',
        help='server mode'
    )
    act_server.set_defaults(func=self.actionServer)

    #
    # action `interface`
    #

    act_runloop = subparsers.add_parser(
        'interface',
        help='show the fzf inteface, remain after choose and switch.'
    )
    act_runloop.set_defaults(func=self.actionInterface)

  def run(self):

    # dispatch tasks
    args = self.parser.parse_args()
    args.func(args)


def run():
  Command().run()
