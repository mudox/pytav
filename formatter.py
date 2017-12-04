#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    'dead_session_line_title': '\033[38;5;65m',
    'dead_session_name': '\033[38;5;242m',
}

cr = '\033[0m'   # reset style
ch = '\033[30m'  # hide foreground into background

fzf_ui_left_margin = 4
fzf_ui_gap = 10


class FZFFormatter:

  def __init__(self, snapshot):
    self.snapshot = snapshot

    self.fzf_ui_width =         \
        fzf_ui_left_margin +    \
        self.snapshot.w_width + \
        fzf_ui_gap +            \
        self.snapshot.s_width

  def fzf_lines(self):
    lines = []

    # live sessions
    for session in self.snapshot.live_sessions:
      lines.append('\n' + self.live_session_line(session))

      if not session.loaded:
        continue

      for window in session.windows:
        lines.append(self.window_line(session.name, window.id, window.name))

    # put all dead sessions into one group
    color = colors['dead_session_line_title']
    line = f'\nnop\t{dead_symbol} {color}Unloaded Sessions{cr}'
    lines.append(line)

    dead_snames = [s.name for s in self.snapshot.dead_sessions]
    for sname in dead_snames:
        lines.append(self.dead_session_line(sname))

    return '\n'.join(lines)

  def window_line(self, session_name, window_id, window_name):
    color1 = colors['window_line_window_name']
    part1 = f'{color1}{window_name}{cr}'
    part1_width = 5 + self.snapshot.w_width + 4  # 5 + 4 for ansi color sequence

    color2 = colors['window_line_session_name']
    part2 = f'{color2}{session_name}{cr}'

    return f'{window_id}\t{ch}⋅{cr} {part1:{part1_width}}{" ":{fzf_ui_gap}}{part2}'

  def dead_session_line(self, session_name):
    color1 = colors['dead_session_name']
    part1 = f'{color1}{session_name}{cr}'

    # INFO!!: color1 use 256 color ansi code, hence 11 long
    part1_width = 11 + self.snapshot.w_width + 4  # 5 + 4 for ansi color sequence

    color2 = colors['window_line_session_name']
    part2 = f'{color2}Load ?{cr}'

    return f'dead\t{ch}⋅{cr} {part1:{part1_width}}{" ":{fzf_ui_gap}}{part2}'

  def live_session_line(self, session):
    symbol = symbols.get(session.name, default_live_symbol)
    color = colors['session_line_live_session_name']

    return f'{session.id}\t{symbol} {color}{session.name}{cr}'
