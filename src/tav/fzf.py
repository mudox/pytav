#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import screen, settings


# TODO: 2 hard corded magic numbers
_minGap = 6
_minWidth = 46

_fzfLeftMargin = 2
_sessionSymbolWidth = 4
_windowSymbolWidth = 2

_loadSessionPrompt = '[Load The Session]'


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

    self._part1Width = max(
        self.snapshot.windowNameMaxWidth,
        self.snapshot.sessionNameMaxWidth,
    )

    self._part2Width = max(
        self.snapshot.sessionNameMaxWidth,
        len(_loadSessionPrompt)
    )

    withoutGap =              \
        _fzfLeftMargin +      \
        _sessionSymbolWidth + \
        _windowSymbolWidth +  \
        self._part1Width +    \
        self._part2Width      \

    withMinGap = withoutGap + _minGap

    self.fzfWidth = max(_minWidth, withMinGap)
    self._gapWidth = self.fzfWidth - withoutGap

    self.fzfHeader = self._fzfHeaderLines()
    self.fzfFeed = self._fzfLines()

  def _height(level):
    """
    - level 0: no empty lines
    - level 1: add empty lines around unlaoded bar
    - level 2: add empty lines between live session lines on the base of level 1
    - level 3: add empty lines between dead session lines on the base of level 2
    - level 4: add empty lines between window lines on the base of level 3
    """
    assert level in range(5)

    # level 0
    fzfHeader = 4
    bareUnloadedBar = 1
    height =                             \
        fzfHeader +                      \
        self.snapshot.windowCount +      \
        self.snapshot.liveSessionCount + \
        bareUnloadedBar +                \
        self.deadSessionCount

    if level == 0:
      return height

    height += 2  # empty line around unloaded bar
    if level == 1:
      return height

    height += self.snapshot.liveSessionCount - 1
    if level == 2:
      return height

    height += self.snapshot.deadSessionCount - 1
    if level == 3:
      return height

    height += self.snapshot.windowCount
    if level == 4:
      return height

  def _unloadedBar(self):
    color = settings.colors.unloadedBar
    symbol = settings.symbols.unloaded
    if ord(symbol) > 0x10000:
      symbolPart = f'  {symbol}   '
    else:
      symbolPart = f'  {symbol}  '
    body = f' ──────{symbolPart}────── '.center(self.fzfWidth)
    line = f'\n{"<nop>":{self._part1Width}}\t{screen.sgr(body, color)}'
    return line

  def _fzfHeaderLines(self):
    lines = '{} sessions ({} alive, {} dead), {} windows'.format(
        self.snapshot.liveSessionCount +
        self.snapshot.deadSessionCount,
        self.snapshot.liveSessionCount,
        self.snapshot.deadSessionCount,
        self.snapshot.windowCount,
    )
    lines += screen.sgrHide('\n·')
    return lines

  def _fzfLines(self):
    lines = []

    #
    # live sessions
    #

    for session in self.snapshot.liveSessions:
      # filter out tav interface session
      if session.name == settings.tmux.tavSessionName:
        continue

      lines.append('\n' + self._liveSessionLine(session))

      for window in session.windows:

        lines.append(self._windowLine(session, window))

    if self.snapshot.deadSessionCount == 0:
      return '\n'.join(lines)

    #
    # unloaded bar
    #

    lines.append(self._unloadedBar())

    #
    # dead sessions
    #

    for session in self.snapshot.deadSessions:
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
    color1 = settings.colors.windowLineWindowName
    part1 = screen.sgr(window.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    # part2
    color2 = settings.colors.windowLineSessionName
    part2 = f'{session.name}:{window.index}'
    part2 = screen.sgr(part2, color2)
    part2 = screen.right(part2, self._part2Width)

    line = hiddenPrefix +            \
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
    symbol = settings.symbols.sessions.get(
        session.name,
        settings.symbols.sessionDefault
    )
    symbol = screen.left(symbol, _sessionSymbolWidth)

    # the only part: session name
    color1 = settings.colors.deadSessionName
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    color2 = settings.colors.deadSessionLineRight
    part2 = screen.sgr('[Load The Session]', color2)
    part2 = screen.right(part2, self._part2Width + _windowSymbolWidth)

    return f'\n{hiddenPrefix}\t{symbol}{part1}{gap}{part2}'

  def _liveSessionLine(self, session):
    hiddenPrefix = f'{session.id:{self._part1Width}}'

    symbol = settings.symbols.sessions.get(
        session.name,
        settings.symbols.sessionDefault
    )
    symbol = screen.left(symbol, _sessionSymbolWidth)

    color1 = settings.colors.sessionLineLiveSessionName
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    part2 = screen.sgrHide('[S]')
    part2 = screen.right(part2, self._part2Width + _windowSymbolWidth)

    return f'{hiddenPrefix}\t{symbol}{part1}{gap}{part2}'
