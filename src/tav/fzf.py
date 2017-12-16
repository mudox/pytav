#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from . import settings

# TODO!: make symbols and colors configurable

symbols = {
    'Configure': '',
    'Update': '',
    'Dashboard': '',
    'Play': '',
}

default_live_symbol = ''
# dead_symbol = ''
dead_symbol = ''

colors = {
    'session_line_live_session_name': '\033[38;5;28m',
    'window_line_window_name': '\033[38;5;81m',
    'window_line_session_name': '\033[38;5;242m',
    'unloaded_bar': '\033[38;5;88m',
    'dead_session_name': '\033[38;5;242m',
}

cr = '\033[0m'  # reset style
ch = '\033[30m'  # hide foreground into background

# TODO: 2 hard corded magic numbers
minGap = 6
minWidth = 46

ansi_pat = re.compile('\x1b\[[^m]+m')

def _color(text, color):
  return f'{color}{text}\x1b[0m'


def _hide(text):
  return f'\x1b[30m{text}\x1b[0m'


def _sgr_width(text):
  chunks = ansi_pat.findall(text)
  return sum([len(c) for c in chunks])


def _screen_width(text):
  return len(text) - _sgr_width(text)


def _left(text, width, fillchar='\x20'):
  return text.ljust(width + _sgr_width(text), fillchar)


def _center(text, width, fillchar='\x20'):
  return text.center(width + _sgr_width(text), fillchar)


def _right(text, width, fillchar='\x20'):
  return text.rjust(width + _sgr_width(text), fillchar)


_fzfLeftMargin = 2
_sessionSymbolWidth = 2
_windowSymbolWidth = 2


class FZFFormatter:

  def __init__(self, snapshot, testMode=False):

    self.snapshot = snapshot
    self.testMode = testMode

    self.part1Width = max(self.snapshot.windowNameMaxWidth,
                          self.snapshot.sessionNameMaxWidth)

    self.part2Width = self.snapshot.sessionNameMaxWidth

    withoutGap =              \
        _fzfLeftMargin        \
        + _sessionSymbolWidth \
        + _windowSymbolWidth  \
        + self.part1Width     \
        + self.part2Width

    withMinGap = withoutGap + minGap

    self.width = max(minWidth, withMinGap)
    self.gap = self.width - withoutGap

  def fzfLines(self):
    lines = []

    #
    # live sessions
    #

    for session in self.snapshot.live_sessions:
      # filter out tav interface session
      if session.name == settings.tavSessionName:
        continue

      lines.append('\n' + self._live_session_line(session))

      for window in session.windows:

        lines.append(self._window_line(session, window))

    #
    # dead sessions
    #

    if self.snapshot.dead_session_count == 0:
      return '\n'.join(lines)

    # unloaded bar
    color = colors['unloaded_bar']
    body = f' UN · LOADED '.center(self.width - 2, '─')
    line = f'\n{"<nop>":{self.part1Width}}\t{color}{body}{cr}\n'
    lines.append(line)

    for session in self.snapshot.dead_sessions:
      lines.append(self._dead_session_line(session))

    if self.testMode:
      return '\n'.join(lines).replace('\x20', '_')
    else:
      return '\n'.join(lines)

  def _window_line(self, session, window):
    hiddenPrefix = f'{window.id:{self.part1Width}}'

    windowSymbol = '· '

    color1 = colors['window_line_window_name']
    part1 = f'{color1}{window.name}{cr}'
    part1 = _left(part1, self.part1Width)

    gap = (self.testMode and '*' or '\x20') * self.gap

    color2 = colors['window_line_session_name']
    part2 = _color(session.name, color2)
    part2 = _right(part2, self.part2Width)

    line =             \
        hiddenPrefix + \
        '\t' +         \
        _hide('⋅⋅') +  \
        windowSymbol + \
        part1 +        \
        gap +          \
        part2

    return line

  def _dead_session_line(self, session):
    hiddenPrefix = f'{session.name:{self.part1Width}}'

    color1 = colors['dead_session_name']
    part1 = _color(session.name, color1)
    part1 = _left(part1, self.part1Width)

    return hiddenPrefix + '\t' + _hide('⋅⋅') + part1

  def _live_session_line(self, session):
    hiddenPrefix = f'{session.id:{self.part1Width}}'

    symbol = symbols.get(session.name, default_live_symbol)
    symbol = _left(symbol, _sessionSymbolWidth)

    color = colors['session_line_live_session_name']
    sessionTitle = _color(session.name, color)

    return f'{hiddenPrefix}\t{symbol}{sessionTitle}'
