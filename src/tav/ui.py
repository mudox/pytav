# -*- coding: utf-8 -*-

import json
import logging
import shlex
import shutil
import subprocess as sp
from functools import reduce
from time import sleep

from . import settings as cfg
from . import core, screen, shell, tmux
from .screen import screenWidth

logger = logging.getLogger(__name__)


def show(oneshot):
  '''
  compose fzf command line, show it centered in current terimnal secreen.
  '''

  try:
    with cfg.paths.interfaceFile.open() as file:
      info = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError) as error:
    logger.warning('''
        error reading interface data from {cfg.paths.interfaceFile}:
        {indent(str(error), '  ')}
        update it first
        ''')
    core.update()
    with cfg.paths.interfaceFile.open() as file:
      info = json.load(file)

  #
  # window background
  #

  if not oneshot:
    shell.run(f'tmux select-pane -P bg={cfg.colors.background}')

  #
  # center fzf ui
  #

  tWidth, _ = shutil.get_terminal_size()
  width = info['fzf']['width']

  hMargin = int((tWidth - width) / 2) + cfg.fzf.hOffset

  #
  # compose fzf command line
  #

  cmd = shlex.split(f'''
    fzf
    --exact

    # hide prefixing tag's
    --with-nth=2..

    # retain the relationship between matched sessions and windows
    --tiebreak=index

    --ansi          # color mode
    --height=100%   # fullscreen mode

    # center interface in the terminal screen
    --margin={cfg.fzf.topMargin},{hMargin},{cfg.fzf.bottomMargin},{hMargin}

    --header='{info["fzf"]["header"]}'
    --inline-info

    # fully transparent background
    --color=bg:-1,bg+:-1
  ''', comments=True)

  if not oneshot:
    # avoid screen flickering
    cmd.append('--no-clear')

    # prevent keys to abort fzf
    for key in ('esc', 'ctrl-c', 'ctrl-g', 'ctrl-q'):
      cmd.append(f'--bind={key}:unix-line-discard')

    # prevent ctrl-z suspend fzf
    cmd.append('--bind=ctrl-z:unix-line-discard')

    cmd.append('--bind=ctrl-t:top')

  #
  # show fzf interface, get user selection
  #

  lines = info['fzf']['lines']

  p = sp.run(
      cmd,
      input=lines.encode(),
      stdout=sp.PIPE
  )

  if p.returncode != 0:
    logger.error('fzf command failed')
    return

  selectedLine = p.stdout.decode().strip()
  tag = selectedLine.split('\t')[0].strip()

  #
  # handle the tag
  #

  # empty separate line
  if len(tag) == 0:
    return

  # live session or window line
  elif tag.startswith('$') or tag.startswith('@'):
    p = tmux.switchTo(tag)
    if p.returncode != -0:
      showMessageCentered('Switching failed, update data ...')
      core.update()
    return

  # other auxiliary lines, e.g. dead sessions group line
  elif tag == '<nop>':
    return

  # handle dead session line
  # TODO!!: split actions into methods
  else:
    try:

      #
      # show creating message
      #

      color = cfg.colors.message
      text = f'Creating session [{tag}] ...'
      text = screen.sgr(text, color)
      showMessageCentered(text)

      #
      # create session
      #

      logger.info(f'load session [{tag}]')
      tmux.hook.disable(f'before creating dead session {tag}')

      path = cfg.paths.sessionsDir / tag
      p = sp.run(
          str(path),
          stdout=sp.DEVNULL,
          stderr=sp.PIPE
      )

      if p.returncode != 0:
        logger.error(f'fail to create session [{tag}]: {p.stderr.decode()}')
        color = cfg.colors.error
        text = f'Creating session [{tag}] FAILED!'
        text = screen.sgr(text, color)
        showMessageCentered(text)
        core.update()
        sleep(1)
        return
      else:
        core.update()
        sleep(1)
        tmux.switchTo(tag)

    finally:
      tmux.hook.enable(f'after creating dead session {tag}')
      showCursor(True)


def showMessageCentered(text):
  # clear screen & hide cursor
  shell.system('clear; tput civis')

  ttyWidth, ttyHeight = shutil.get_terminal_size()

  lines = text.splitlines()
  textHeight = len(lines)
  textWidth = reduce(max, [screenWidth(line) for line in lines])

  x = int((ttyWidth - textWidth) / 2)
  y = int((ttyHeight - textHeight) / 2)

  shell.system(f'tput cup {y} {x}')

  print(text, end=None)


def showCursor(flag):
  if flag:
    shell.system('tput cnorm')
  else:
    shell.system('tput civis')
