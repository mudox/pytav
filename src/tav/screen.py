#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

_sgrPattern = re.compile('\x1b\[[^m]+m')


def sgr(text, color):
  return f'{color}{text}\x1b[0m'

def sgrRGB(text, rgb):
    r, g, b = rgb
    return f'\x1b[38;2;{r};{g};{b}m{text}\x1b[0m'

def sgrHide(text):
  return f'\x1b[30m{text}\x1b[0m'


def sgrWidth(text):
  chunks = _sgrPattern.findall(text)
  return sum([len(c) for c in chunks])


def screenWidth(text):
  return len(text) - sgrWidth(text)


def left(text, width, fillchar='\x20'):
  return text.ljust(width + sgrWidth(text), fillchar)


def center(text, width, fillchar='\x20'):
  return text.center(width + sgrWidth(text), fillchar)


def right(text, width, fillchar='\x20'):
  return text.rjust(width + sgrWidth(text), fillchar)
