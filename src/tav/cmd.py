#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from jaclog import jaclog

from . import core, settings, tests, tmux

__version__ = '2.0.1'

jaclog.configure(
    appName='tav',
    fileName='tav.log',
    logTTY=settings.paths.logTTY,
    compact=True
)
logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


class Command:

  def snapshot(self, args):
    settings.action = 'snapshot'
    logger.debug('invoked to perform action: [snapshot]')

    core.update()

  def oneshot(self, args):
    settings.action = 'oneshot'
    logger.debug('invoked to perform action: [oneshot]')

    core.update()
    core.start_ui(oneshot=True)

  def serve(self, args):
    logger.debug('invoked to perform action: [serve]')
    settings.action = 'serve'

    while True:
      core.start_ui(oneshot=False)

  def hook(self, args):
    settings.action = 'hook'

    if args.hookEnabled is None:
      if args.event is None:
        msg = 'must specify either the trigger event type or [-d|-e] option\n\n'
        msg += self.parser.format_usage()
        logger.warn(msg)
        return

      settings.hookEvent = args.event

      msg = f'invoked to perform action: [hook]'
      msg += f'\ntriggered by: [{args.event}]'
      logger.debug(msg)

      tmux.prepareTmuxInterface(force=False)
      tmux.hook.run()

    else:
      msg = f'invoked to perform action: [hook]'
      msg += f'\n{args.hookEnabled and "enable" or "disable"} hook update'
      logger.debug(msg)

      if args.hookEnabled:
        tmux.hook.enable()
      else:
        tmux.hook.disable()

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

    self.parser.add_argument('--version', action='version', version=__version__)

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

    # action `hook`
    act_hook = subparsers.add_parser(
        'hook', aliases=['h', 'hk', 'ho'],
        help='''
        update snapshot and update the fzf interface in tmux window
        '''
    )

    # hook {-d | -e}
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
    group.add_argument(
        'event',
        nargs='?',
        choices=[
            'window-linked',
            'window-renamed',
            'window-unlinked',
            'session-renamed'],
        help='event type that triggers the hook')
    act_hook.set_defaults(func=self.hook, hookEnabled=None)

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
