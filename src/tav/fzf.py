#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import screen, settings

# TODO!: make symbols and colors configurable

# _symbols = {
# 'Console': '',
# 'Update': '',
# 'Dashboard': '',
# 'Play': '',
# }
# _defaultLiveSessionSymbol = ''
# _defaultDeadSessionSymbol = ''

# _colors = {
# 'sessionLineLiveSessionName': '\033[38;5;28m',
# 'windowLineWindowName': '\033[38;5;81m',
# 'windowLineSessionName': '\033[38;5;242m',
# 'unloadedBar': '\033[38;5;88m',
# 'deadSessionName': '\033[38;5;242m',
# }


_symbols = '''
    Console     : 🐬
    Update      : 🎉
    Dashboard   : 🌿
    Play        : ⛑
    Tav-Project : 🦊
    Frameworks  : 🍄
'''
_symbols = [s.split(':') for s in _symbols.strip().splitlines()]
_symbols = {s[0].strip(): s[1].strip() for s in _symbols}

# a non-space character prevent fzf from strip the indentation
_defaultLiveSessionSymbol = screen.sgrHide('·')
_defaultDeadSessionSymbol = '👻 '

_colors = {
    'sessionLineLiveSessionName': '\033[32m',
    'windowLineWindowName': '\033[34m',
    'windowLineSessionName': '\033[38;5;242m',
    'unloadedBar': '\033[38;5;88m',
    'deadSessionName': '\033[38;5;242m',
}

# TODO: 2 hard corded magic numbers
_minGap = 6
_minWidth = 46

_fzfLeftMargin = 2
_sessionSymbolWidth = 4
_windowSymbolWidth = 2


class FZFFormatter:

  def __init__(self, snapshot, testMode=False):

    self.snapshot = snapshot
    self.testMode = testMode

    self._sessionSymbolPadding = screen.sgrHide('⋅' * _sessionSymbolWidth)

    self.part1Width = max(self.snapshot.windowNameMaxWidth,
                          self.snapshot.sessionNameMaxWidth)

    self.part2Width = self.snapshot.sessionNameMaxWidth

    withoutGap =              \
        _fzfLeftMargin        \
        + _sessionSymbolWidth \
        + _windowSymbolWidth  \
        + self.part1Width     \
        + self.part2Width

    withMinGap = withoutGap + _minGap

    self.width = max(_minWidth, withMinGap)
    self.gap = self.width - withoutGap
    self.fzfHeader = self._fzfHeaderLines()

  def unloadedBar(self):
    color = _colors['unloadedBar']
    body = f' ──────  {_defaultDeadSessionSymbol}  ────── '.center(self.width - 2)
    line = f'\n{"<nop>":{self.part1Width}}\t{screen.sgr(body, color)}\n'
    return line

  def _fzfHeaderLines(self):
    lines = '{} sessions ({} alive, {} dead), {} windows'.format(
        self.snapshot.live_session_count +
        self.snapshot.dead_session_count,
        self.snapshot.live_session_count,
        self.snapshot.dead_session_count,
        self.snapshot.window_count,
    )
    lines += screen.sgrHide('\n·')
    return lines
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

    if self.snapshot.dead_session_count == 0:
      return '\n'.join(lines)

    #
    # unloaded bar
    #

    lines.append(self.unloadedBar())

    #
    # dead sessions
    #

    for session in self.snapshot.dead_sessions:
      lines.append(self._dead_session_line(session))

    if self.testMode:
      return '\n'.join(lines).replace('\x20', '_')
    else:
      return '\n'.join(lines)

  def _window_line(self, session, window):
    # prefix
    hiddenPrefix = f'{window.id:{self.part1Width}}'

    # window symbol
    windowSymbol = '· '

    # part1
    color1 = _colors['windowLineWindowName']
    part1 = screen.sgr(window.name, color1)
    part1 = screen.left(part1, self.part1Width)

    # gap
    gap = (self.testMode and '*' or '\x20') * self.gap

    # part2
    color2 = _colors['windowLineSessionName']
    part2 = screen.sgr(session.name, color2)
    part2 = screen.right(part2, self.part2Width)

    line =                           \
        hiddenPrefix +               \
        '\t' +                       \
        self._sessionSymbolPadding + \
        windowSymbol +               \
        part1 +                      \
        gap +                        \
        part2

    return line

  def _dead_session_line(self, session):
    # prefix
    hiddenPrefix = f'{session.name:{self.part1Width}}'

    # session symbol if any
    symbol = _symbols.get(session.name, _defaultLiveSessionSymbol)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    # the only part: session name
    color1 = _colors['deadSessionName']
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self.part1Width)

    return f'\n{hiddenPrefix}\t{symbol}{part1}'

  def _live_session_line(self, session):
    hiddenPrefix = f'{session.id:{self.part1Width}}'

    symbol = _symbols.get(session.name, _defaultLiveSessionSymbol)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    color = _colors['sessionLineLiveSessionName']
    sessionTitle = screen.sgr(session.name, color)

    return f'{hiddenPrefix}\t{symbol}{sessionTitle}'
