#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import textwrap

from . import settings

_symbols = {
    logging.ERROR: ' ',
    logging.WARNING: ' ',
    logging.INFO: ' ',
    logging.DEBUG: ' ',
    'verbose': ' ',
}

_colors = {
    logging.ERROR: ((200, 0, 0), (255, 255, 255)),
    logging.WARNING: ((255, 87, 191), (255, 255, 255)),
    logging.INFO: ((255, 224, 102), (255, 255, 255)),
    logging.DEBUG: ((64, 255, 64), (255, 255, 255)),
    'fileFuncName': ((155, 155, 155), (130, 130, 130)),
    # 'time_sep': ((130, 130, 130), (70, 70, 70)),
}


def _colorize(text, rgb):
  r, g, b = rgb
  return f'\033[38;2;{r};{g};{b}m{text}\033[0m'


def configureLogging():
  lines = f'------------ {datetime.datetime.now()} ------------'
  lines = f'\n\n\n{lines}\n\n\n'

  rootLogger = logging.getLogger()
  rootLogger.setLevel(logging.NOTSET)

  formatter = ConsoleLogFormatter()

  # log to file
  logToFile = logging.FileHandler(str(settings.paths.logFile))
  logToFile.setFormatter(formatter)
  rootLogger.addHandler(logToFile)

  with settings.paths.logFile.open('a') as file:
    file.write(lines)

  # log to tty
  if settings.paths.logTTY is not None:
    logToTTY = logging.FileHandler(settings.paths.logTTY)
    logToTTY.setFormatter(formatter)
    rootLogger.addHandler(logToTTY)

    with open(settings.paths.logTTY, 'w') as file:
      file.write(lines)

  else:
    rootLogger.error('Log window not found, TTY logger can not be created')

  rootLogger.info('Logging initialized')


class ConsoleLogFormatter(logging.Formatter):

  def __init__(self):
    super().__init__()
    self.lastHeadLine = ''

  def format(self, record):

    # head line
    color = _colors[record.levelno]
    symbol = _symbols[record.levelno]
    subsystem = (record.name == '__main__') and 'main' or record.name
    head1 = _colorize(f'{symbol}{subsystem}', color[0])

    color = _colors['fileFuncName']
    head2 = _colorize(f'[{record.filename}] {record.funcName}', color[1])

    headLine = f'{head1} {head2}'

    # body
    message = super().format(record)
    message = textwrap.indent(message, '\x20' * 2)

    # combine
    if headLine != self.lastHeadLine:
      lines = f'\n{headLine}\n{message}'
      self.lastHeadLine = headLine
    else:
      lines = f'\n{message}'

    # indent 1 space for the sake of aesthetic
    lines = textwrap.indent(lines, '\x20')
    return lines
