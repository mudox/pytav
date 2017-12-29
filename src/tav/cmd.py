#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from contextlib import suppress

from . import core, ui
from .diagnose import diagnose
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
      core.updateModel()
      tavSession.refresh(forceRecreate=True)
      startServer()

  def actionInterface(self, args):
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
        description='without any action is equivalent to `oneshot`')

    #
    # action `oneshot`
    #

    act_oneshot = subparsers.add_parser(
        'oneshot', help='the default action, show fzf inteface once')
    act_oneshot.set_defaults(func=self.actionOneshot)

    #
    # action: `diagnose`
    #

    act_oneshot = subparsers.add_parser(
        'diagnose', aliases=['d', 'dia'], help='dump diagnose infomation')
    act_oneshot.set_defaults(func=diagnose)

    #
    # action `server`
    #

    act_server = subparsers.add_parser(
        'server', help='start Tav server daemon')
    act_server.set_defaults(func=self.actionServer)

    #
    # action `interface`
    #

    act_runloop = subparsers.add_parser(
        'interface', help='show the fzf inteface')
    act_runloop.set_defaults(func=self.actionInterface)

  def run(self):

    # dispatch tasks
    args = self.parser.parse_args()
    args.func(args)


def run():
  Command().run()
