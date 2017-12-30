#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from contextlib import suppress

from . import core, diagnose, ui, watcher
from .server import start as startServer
from .tmux import tavSession

__version__ = '3.1'

logger = logging.getLogger(__name__)

#
# actions (sub-commands)
#


class Command:

  def actionOneshot(self, args):
    ui.show(oneshot=True)

  def actionServer(self, args):
    with suppress(KeyboardInterrupt):
      core.updateModel()  # update server-side model
      tavSession.swapYinYang(force=True)
      startServer()

  def actionRunloop(self, args):
    watcher.startMonitoring()

    while True:
      ui.show(oneshot=False)

  def actionDiagnose(self, args):
    diagnose.dump(args.targets)

    while True:
      ui.show(oneshot=False)

  #
  # CLI interface
  #

  def __init__(self):

    self.parser = argparse.ArgumentParser(
        prog='tav',
        description='An tmux `choose-tree` replacement powered by fzf action.')
    # defaults to update and choose once
    self.parser.set_defaults(func=self.actionOneshot)

    self.parser.add_argument(
        '--version', action='version', version=__version__)

    #
    # actions
    #

    subparsers = self.parser.add_subparsers(
        title='actions',
        description='without any action is equivalent to `oneshot`',
    )

    #
    # action `oneshot`
    #

    cmdOneshot = subparsers.add_parser(
        'oneshot',
        help='the default action, show fzf inteface once',
    )
    cmdOneshot.set_defaults(func=self.actionOneshot)

    #
    # action: `diagnose`
    #

    cmdDiagnose = subparsers.add_parser(
        'diagnose',
        aliases=['d', 'dia'],
        help='dump diagnose infomation',
    )
    cmdDiagnose.set_defaults(func=self.actionDiagnose)

    cmdDiagnose.add_argument(
        'targets',
        nargs='?',
        default=[],
        action='append',
        help='the infomation that is to be dumped to the stdout',
    )

    #
    # action `server`
    #

    cmdServer = subparsers.add_parser(
        'server',
        help='start Tav server daemon',
    )
    cmdServer.set_defaults(func=self.actionServer)

    #
    # action `runloop`
    #

    cmdRunloop = subparsers.add_parser(
        'runloop',
        help='show interface in runloop mode',
    )
    cmdRunloop.set_defaults(func=self.actionRunloop)

  def run(self):

    # dispatch tasks
    args = self.parser.parse_args()
    args.func(args)


def run():
  Command().run()
