# -*- coding: utf-8 -*-

import logging
import textwrap

from . import screen
from . import settings as cfg

logger = logging.getLogger(__name__)

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

    # calculate widths

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

    withMinGap = withoutGap + cfg.fzf.minGap

    self.fzfWidth = max(cfg.fzf.minWidth, withMinGap)
    self._gapWidth = self.fzfWidth - withoutGap

    # determine height
    self.layoutLevel = cfg.fzf.layoutLevel
    ttyHeight = self.snapshot.ttyHeight
    if self.layoutLevel == 'auto':
      logger.debug(f'terminal height:  [{ttyHeight}]')

      for lvl in range(5):
        height = self._height(level=lvl)
        logger.debug(f'height at level {lvl}: {height}')
        if height > ttyHeight:
          self.layoutLevel = max(0, lvl - 1)
          logger.debug('break\n')
          break
      else:
        self.layoutLevel = 4

    self.fzfHeader = self._fzfHeaderLines()
    self.fzfFeed = self._fzfLines()

    logger.debug(textwrap.dedent(f'''\
        final layout level:  [{self.layoutLevel}]
        final screen height: {len(self.fzfFeed.splitlines()) + (2 * cfg.fzf.yMargin) + 4}
        estimated height:    {self._height(self.layoutLevel)}\
    '''))

  def _height(self, level):
    """
    - level 0: no empty lines
    - level 1: add empty lines around unlaoded bar
    - level 2: add empty lines between live session lines on the base of level 1
    - level 3: add empty lines between dead session lines on the base of level 2
    - level 4: add empty lines between window lines on the base of level 3
    """
    assert level in range(5)

    # level 0
    fzfHeader = 3 + 1  # 1st line must be empty line
    bareUnloadedBar = 1
    height =                             \
        cfg.fzf.yMargin * 2 +       \
        fzfHeader +                      \
        self.snapshot.windowCount +      \
        self.snapshot.liveSessionCount + \
        bareUnloadedBar +                \
        self.snapshot.deadSessionCount

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
    symbol = cfg.symbols.unloaded
    symbolCode = ord(symbol)

    symbolColor = cfg.colors.unloadedBarSymbol
    symbol = screen.sgr(symbol, symbolColor)

    # adjust alignment for emoji symbols
    if symbolCode > 0x10000:
      symbolPart = f'  {symbol}   '
    else:
      symbolPart = f'  {symbol}  '

    barColor = cfg.colors.unloadedBar
    wing = screen.sgr('──────', barColor)
    line = screen.center(f'{wing}{symbolPart}{wing}', self.fzfWidth)
    line = f'{"<nop>":{self._part1Width}}\t{screen.sgr(line, barColor)}'
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
    lines = ['']

    #
    # live sessions
    #

    for idx, session in enumerate(self.snapshot.liveSessions):
      # filter out tav interface session
      if session.name == cfg.tmux.tavSessionName:
        continue

      if self.layoutLevel >= 2 and idx > 0:
        lines.append('')

      lines.append(self._liveSessionLine(session))

      for window in session.windows:
        if self.layoutLevel >= 4:
          lines.append('')
        lines.append(self._windowLine(session, window))

    if self.snapshot.deadSessionCount == 0:
      return '\n'.join(lines)

    #
    # unloaded bar
    #

    if self.layoutLevel >= 1:
      lines += ['', self._unloadedBar(), '']
    else:
      lines.append(self._unloadedBar())

    #
    # dead sessions
    #

    for idx, session in enumerate(self.snapshot.deadSessions):
      if self.layoutLevel >= 3 and idx > 0:
        lines.append('')
      lines.append(self._deadSessionLine(session))

    if self._testMode:
      return '\n'.join(lines).replace('\x20', '_')
    else:
      return '\n'.join(lines)

  def _windowLine(self, session, window):
    # prefix
    hiddenPrefix = f'{window.id:{self._part1Width}}'

    # window symbol
    windowSymbol = cfg.symbols.windowDefault
    windowSymbol = screen.sgr(windowSymbol, cfg.colors.windowSymbol)
    windowSymbol = screen.left(windowSymbol, _windowSymbolWidth)

    # part1
    color1 = cfg.colors.windowLineLeft
    part1 = screen.sgr(window.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    # part2
    color2 = cfg.colors.windowLineRight
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
    symbol = cfg.symbols.sessions.get(
        session.name,
        cfg.symbols.sessionDefault
    )
    symbolColor = cfg.colors.deadSessionSymbol
    symbol = screen.sgr(symbol, symbolColor)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    # the only part: session name
    color1 = cfg.colors.deadSessionLineLeft
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    color2 = cfg.colors.deadSessionLineRight
    # part2 = screen.sgr('', color2)
    part2 = screen.sgr('load ', color2)
    part2 = screen.right(part2, self._part2Width + _windowSymbolWidth)

    return f'{hiddenPrefix}\t{symbol}{part1}{gap}{part2}'

  def _liveSessionLine(self, session):
    hiddenPrefix = f'{session.id:{self._part1Width}}'

    symbol = cfg.symbols.sessions.get(
        session.name,
        cfg.symbols.sessionDefault
    )
    symbolColor = cfg.colors.liveSessionSymbol
    symbol = screen.sgr(symbol, symbolColor)
    symbol = screen.left(symbol, _sessionSymbolWidth)

    color1 = cfg.colors.liveSessionLineLeft
    part1 = screen.sgr(session.name, color1)
    part1 = screen.left(part1, self._part1Width)

    # gap
    gap = ('*' if self._testMode else '\x20') * self._gapWidth

    color = screen.color2sgr(cfg.colors.background)
    part2 = screen.sgr('[S]', color)
    part2 = screen.right(part2, self._part2Width + _windowSymbolWidth)

    return f'{hiddenPrefix}\t{symbol}{part1}{gap}{part2}'
