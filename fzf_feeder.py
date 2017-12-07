#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import settings

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

fzf_left_margin = 2
fzf_session_symbol_padding = 2
fzf_window_symbol_padding = 2

# TODO: 2 hard corded magic numbers
fzf_min_gap = 6
fzf_min_width = 46

ansi_pat = re.compile('\x1b\[[^m]+m')


def _width(text):
  chunks = ansi_pat.findall(text)
  return sum([len(c) for c in chunks])


def _left(text, width, fillchar='\x20'):
  return text.ljust(width + _width(text), fillchar)


def _center(text, width, fillchar='\x20'):
  return text.center(width + _width(text), fillchar)


def _right(text, width, fillchar='\x20'):
  return text.rjust(width + _width(text), fillchar)


class FZFFormatter:

  def __init__(self, snapshot):

    self.snapshot = snapshot

    self.fzf_field_1_width = max(self.snapshot.wname_max_width,
                                 self.snapshot.sname_max_width)

    self.fzf_field_2_width = self.snapshot.sname_max_width

    without_gap =                    \
        fzf_left_margin              \
        + fzf_session_symbol_padding \
        + fzf_window_symbol_padding  \
        + self.fzf_field_1_width     \
        + self.fzf_field_2_width
    with_min_gap = without_gap + fzf_min_gap

    self.fzf_width = max(fzf_min_width, with_min_gap)
    self.fzf_gap = self.fzf_width - without_gap

  def fzf_lines(self):
    lines = []

    #
    # live sessions
    #

    for session in self.snapshot.live_sessions:
      # filter out tav interface session
      if session.name == settings.tav_session_name:
        continue

      lines.append('\n' + self.live_session_line(session))

      for window in session.windows:

        lines.append(self.window_line(session, window))

    #
    # dead sessions
    #

    if self.snapshot.dead_session_count == 0:
      return '\n'.join(lines)

    # unloaded bar
    color = colors['unloaded_bar']
    body = f' UN · LOADED '.center(self.fzf_width - 2, '─')
    # line = f'\n{"<nop>":{self.snapshot.sname_max_width}}\t{ch}⋅⋅{cr}{color}{body}{cr}\n'
    line = f'\n{"<nop>":{self.snapshot.sname_max_width}}\t{color}{body}{cr}\n'
    lines.append(line)

    for session in self.snapshot.dead_sessions:
      lines.append(self.dead_session_line(session))

    return '\n'.join(lines)

  def window_line(self, session, window):
    color1 = colors['window_line_window_name']
    part1 = f'{color1}{window.name}{cr}'
    part1 = _left(part1, self.fzf_field_1_width)

    color2 = colors['window_line_session_name']
    part2 = f'{color2}{session.name}{cr}'
    part2 = _right(part2, self.fzf_field_2_width)

    line = f'{window.id:{self.fzf_field_1_width}}' + \
            f'\t{ch}⋅⋅{cr}· ' +                      \
            f'{part1}' +                             \
            f'{" " * self.fzf_gap}' +                \
            f'{part2}'

    return line

  def dead_session_line(self, session):
    # field1
    color1 = colors['dead_session_name']
    part1 = f'{color1}{session.name}{cr}'
    part1 = _left(part1, self.fzf_field_1_width)

    return f'{session.name:{self.fzf_field_1_width}}' + \
            f'\t{ch}⋅⋅{cr}' +                           \
            f'{part1}'

  def live_session_line(self, session):
    symbol = symbols.get(session.name, default_live_symbol)
    color = colors['session_line_live_session_name']

    return f'{session.id:{self.snapshot.sname_max_width}}\t{symbol} {color}{session.name}{cr}'
