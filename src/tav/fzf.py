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
# '_unloadedBar': '\033[38;5;88m',
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
    'unloadedBar': '\033[38;5;20m',
    'deadSessionName': '\033[38;5;242m',
}

# TODO: 2 hard corded magic numbers
_minGap = 6
_minWidth = 46

_fzfLeftMargin = 2
_sessionSymbolWidth = 4
_windowSymbolWidth = 2


class FZFFormatter:
  """ Transfer information from `tmux.Snapshot` object into fzf source lines.

  Attributes:
    snapshot (tmux.Snapshot): The source snapshot object.
    fzfWidth (int): Screen width of fzf interface.
    fzfHeader (str): Passed to `fzf --header` option.
    fzfFeed (str): Lines feed as stdin of `fzf`.

  """

  def __init__(self, snapshot, testMode=False):

    self.snapshot = snapshot
    self._testMode = testMode

    self._sessionSymbolPadding = screen.sgrHide('⋅' * _sessionSymbolWidth)

    self._part1Width = max(self.snapshot.windowNameMaxWidth,
                           self.snapshot.sessionNameMaxWidth)

    self._part2Width = self.snapshot.sessionNameMaxWidth

    withoutGap =              \
        _fzfLeftMargin        \
        + _sessionSymbolWidth \
        + _windowSymbolWidth  \
        + self._part1Width    \
        + self._part2Width

    withMinGap = withoutGap + _minGap

    self.fzfWidth = max(_minWidth, withMinGap)
    self._gap = self.fzfWidth - withoutGap

    self.fzfHeader = self._fzfHeaderLines()
    self.fzfFeed = self._fzfLines()

  def _unloadedBar(self):
    color = _colors['unloadedBar']
    body = f' ──────  {_defaultDeadSessionSymbol}  ────── '.center(self.fzfWidth - 2)
    line = f'\n{"<nop>":{self._part1Width}}\t{screen.sgr(body, color)}'
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

  def _fzfLines(self):
    lines = []

    #
    # live sessions
    #

    for session in self.snapshot.live_sessions:
      # filter out tav interface session
      if session.name == settings.tavSessionName:
        continue

      lines.append('\n' + self._liveSessionLine(session))

      for window in session.windows:

        lines.append(self._windowLine(session, window))

    if self.snapshot.dead_session_count == 0:
      return '\n'.join(lines)

    #
    # unloaded bar
    #

    lines.append(self._unloadedBar())

    #
    # dead sessions
    #

    for session in self.snapshot.dead_sessions:
      lines.append(self._deadSessionLine(session))

    if self._testMode:
      return '\n'.join(lines).replace('\x20', '_')
    else:
      return '\n'.join(lines)

  def _windowLine(self, session, window):
    # prefix
    hiddenPrefix = f'{window.id:{self._part1Width}}'

    # window symbol
    windowSymbol = '· '

    # part1
    color1 = _colors['windowLineWindowName']
    part1 = screen.sgr(window.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = (self._testMode and '*' or '\x20') * self._gap

    # part2
    color2 = _colors['windowLineSessionName']
    part2 = screen.sgr(session.name, color2)
    part2 = screen.right(part2, self._part2Width)

    line =                           \
        hiddenPrefix +               \
        '\t' +                       \
        self._sessionSymbolPadding + \
        windowSymbol +               \
        part1 +                      \
        gap +                        \
        part2

    return line

  def _deadSessionLine(self, session):
    # prefix
    hiddenPrefix = f'{session.name:{self._part1Width}}'

    # session symbol if any
    symbol = _symbols.get(session.name, _defaultLiveSessionSymbol)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    # the only part: session name
    color1 = _colors['deadSessionName']
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self._part1Width)

    return f'\n{hiddenPrefix}\t{symbol}{part1}'

  def _liveSessionLine(self, session):
    hiddenPrefix = f'{session.id:{self._part1Width}}'

    symbol = _symbols.get(session.name, _defaultLiveSessionSymbol)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    color = _colors['sessionLineLiveSessionName']
    sessionTitle = screen.sgr(session.name, color)

    return f'{hiddenPrefix}\t{symbol}{sessionTitle}'
