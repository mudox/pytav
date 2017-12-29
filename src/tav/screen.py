# -*- coding: utf-8 -*-

import re

_r = '\033[0m'  # reset style
_h = '\033[30m'  # hide foreground into background

sgrPattern = re.compile('\x1b\[[^m]+m')


def sgr(text, color):
  return f'{color}{text}\x1b[0m'


_colorMapping_ = {
    'black': '\x1b[30m',
    'red': '\x1b[31m',
    'green': '\x1b[32m',
    'yellow': '\x1b[33m',
    'blue': '\x1b[34m',
    'magenta': '\x1b[35m',
    'cyan': '\x1b[36m',
    'white': '\x1b[37m',
}


def color2sgr(color):
  if isinstance(color, str):
    color = color.lower()

    # Hex digits
    if color.startswith('#'):
      try:
        if len(color) == 4:
          r = int(color[1] * 2, base=16)
          g = int(color[2] * 2, base=16)
          b = int(color[3] * 2, base=16)
          return f'\x1b[38;2;{r};{g};{b}m'
        elif len(color) == 7:
          r = int(color[1:3], base=16)
          g = int(color[3:5], base=16)
          b = int(color[5:7], base=16)
          return f'\x1b[38;2;{r};{g};{b}m'
        else:
          pass
      except BaseException:
        pass

    # 'red`, `green` ...
    if color in _colorMapping_:
      return _colorMapping_[color]

    # `255, 23, 192`
    m = re.match(r'^(\d+)\s*,\s*(\d+)\s*,\s*(\d+)$', color)
    if m is not None:
      r, g, b = m.groups()
      return f'\x1b[38;2;{r};{g};{b}m'

    # from `0` to ~ `255`
    try:
      if int(color) in range(256):
        return f'\x1b[38;5;{color}m'
      else:
        return None
    except BaseException:
      return None

  elif isinstance(color, int) and color in range(256):
    return f'\x1b[38;5;{color}m'

  else:
    return None


def sgrHide(text):
  return f'\x1b[30m{text}\x1b[0m'


def sgrWidth(text):
  chunks = sgrPattern.findall(text)
  return sum([len(c) for c in chunks])


def screenWidth(text):
  return len(text) - sgrWidth(text)


def left(text, width, fillchar='\x20'):
  return text.ljust(width + sgrWidth(text), fillchar)


def center(text, width, fillchar='\x20'):
  return text.center(width + sgrWidth(text), fillchar)


def right(text, width, fillchar='\x20'):
  return text.rjust(width + sgrWidth(text), fillchar)
