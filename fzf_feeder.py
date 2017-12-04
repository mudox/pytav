#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    'session_line_live_session_name': '\033[32m',
    'window_line_window_name': '\033[34m',
    'window_line_session_name': '\033[38;5;242m',
    'unloaded_bar': '\033[38;5;88m',
    'dead_session_name': '\033[38;5;242m',
}

cr = '\033[0m'   # reset style
ch = '\033[30m'  # hide foreground into background

fzf_ui_left_margin = 4
fzf_ui_gap = 10


class FZFFormatter:

  def __init__(self, snapshot):
    self.snapshot = snapshot

    self.fzf_field_1_width = self.snapshot.w_width
    self.fzf_field_2_width = max(self.snapshot.s_width, 20)

    self.fzf_ui_width =          \
        fzf_ui_left_margin +     \
        self.fzf_field_1_width + \
        fzf_ui_gap +             \
        self.fzf_field_2_width

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

    if len(self.snapshot.dead_sessions) == 0:
      return

    # unloaded bar
    color = colors['unloaded_bar']
    body = f' UN  {dead_symbol}  LOADED '.center(self.fzf_ui_width, '─')[:-1]
    line = f'\n{"<nop>":{self.snapshot.s_width}}\t{color}{body}{cr}\n'
    lines.append(line)

    for session in self.snapshot.dead_sessions:
      lines.append(self.dead_session_line(session))

    return '\n'.join(lines)

  def window_line(self, session, window):
    color1 = colors['window_line_window_name']
    part1 = f'{color1}{window.name}{cr}'
    width1 = 5 + self.snapshot.w_width + 4  # 5 + 4 for ansi color sequence

    color2 = colors['window_line_session_name']
    part2 = f'{color2}{session.name}{cr}'
    width2 = 11 + self.fzf_field_2_width + 4  # 11 + 4 for 256-color ansi sequence

    return f'{window.id:{self.snapshot.s_width}}' + \
            f'\t{ch}⋅⋅{cr}' +                        \
            f'{part1:{width1}}' +                   \
            f'{" ":{fzf_ui_gap}}' +                 \
            f'{part2:>{width2}}'

  def dead_session_line(self, session):
    # field1
    color1 = colors['dead_session_name']
    part1 = f'{color1}{session.name}{cr}'
    width1 = 11 + self.fzf_field_1_width + 4  # 11 + 4 for 256-color ansi sequence

    # field2
    color2 = colors['window_line_session_name']
    part2 = f'{color2}<Select to Load>{cr}'
    width2 = 11 + self.fzf_field_2_width + 4  # 11 + 4 for 256-color ansi sequence

    return f'{session.name:{self.snapshot.s_width}}' + \
            f'\t{ch}⋅⋅{cr}' +                           \
            f'{part1:{width1}}' +                      \
            f'{" ":{fzf_ui_gap}}' +                    \
            f'{part2:>{width2}}'

  def live_session_line(self, session):
    symbol = symbols.get(session.name, default_live_symbol)
    color = colors['session_line_live_session_name']

    return f'{session.id:{self.snapshot.s_width}}\t{symbol} {color}{session.name}{cr}'
