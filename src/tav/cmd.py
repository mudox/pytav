#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from . import core, tmux
from .settings import cfg
from .diagnose import diagnose

__version__ = '2.2.3'

logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


class Command:

  def actionCC(self, args):
    if args.print:
      if tmux.isTavSessionReady():
        print('Tav session is ready')
      else:
        print('Tav session is NOT ready')

    core.makeTavSession(args.force)

  def actionOneshot(self, args):
    core.update()
    core.show(oneshot=True)

  def actionAttach(self, args):
    core.update()
    core.makeTavSession()
    tmux.refreshFinderWindow()
    tmux.switchTo(cfg.tmux.finderWindowTarget)

  def actionServe(self, args):
    while True:
      core.show(oneshot=False)

  def actionHook(self, args):
    if args.hookOption is None:  # perform hook update

      # must specify event type or arbitrary reason
      if args.event is None:
        msg = 'must specify either the trigger event type or [-d|-e] option\n\n'
        msg += self.parser.format_usage()
        print(msg)
        return

      cfg.hookEvent = args.event

      core.makeTavSession()
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

    # action `attach`
    act_attach = subparsers.add_parser(
        'attach', aliases=['a', 'at'],
        help='update backing data, and switch to Tav finder window'
    )
    act_attach.set_defaults(func=self.actionAttach)

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
    act_hook.set_defaults(func=self.actionHook, hookOption=None)

    # action `oneshot`
    act_oneshot = subparsers.add_parser(
        'oneshot',
        help='''
        make a new snapshot and show the fzf interface, close after choose and
        switch. this is the DEFAULT action
        '''
    )
    act_oneshot.set_defaults(func=self.actionOneshot)

    # action: `diagnose`
    act_oneshot = subparsers.add_parser(
        'diagnose', aliases=['d', 'dia'],
        help='dump diagnose infomation'
    )
    act_oneshot.set_defaults(func=diagnose)

    # action `serve`
    act_serve = subparsers.add_parser(
        'serve', aliases=['srv'],
        help='show the fzf inteface, remain after choose and switch.'
    )
    act_serve.set_defaults(func=self.actionServe)

    # action `cc`
    act_cc = subparsers.add_parser(
        'cc',
        help='check and create the Tav session if needed, or create it no matter if it is already ready'
    )
    act_cc.add_argument(
        '-f', '--force',
        action='store_true',
        help='force recreating the session'
    )
    act_cc.add_argument(
        '-p', '--print',
        action='store_true',
        help='print checking result'
    )
    act_cc.set_defaults(func=self.actionCC)

  def run(self):

    # dispatch tasks
    args = self.parser.parse_args()
    args.func(args)


def run():
  Command().run()
