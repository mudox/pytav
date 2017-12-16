#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

_symbols = {
    'Configure': '',
    'Update': '',
    'Dashboard': '',
    'Play': '',
}

_r = '\033[0m'   # reset style
_h = '\033[30m'  # hide foreground into background

sgrPattern = re.compile('\x1b\[[^m]+m')


def sgr(text, color):
  return f'{color}{text}\x1b[0m'


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
