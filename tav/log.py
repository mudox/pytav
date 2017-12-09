#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import textwrap

import settings

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

  def format(self, record):

    # head line
    symbol = _symbols[record.levelno]
    color = _colors[record.levelno]
    subsystem = (record.name == '__main__') and 'main' or record.name
    head = _colorize(f'{symbol}{subsystem}', color[0])

    color = _colors['fileFuncName']
    fileFuncName = _colorize(f'[{record.filename}] {record.funcName}', color[1])

    # body
    message = super().format(record)
    message = textwrap.indent(message, '\x20' * 2)

    # combine
    lines = f'\n{head} {fileFuncName}\n{message}'
    lines = textwrap.indent(lines, '\x20')  # indent 1 space for aethetics

    return lines
