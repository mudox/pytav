#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO!: make symbols and colors configurable

symbols = {
    'Configure': '',
    'Update': '',
    'Dashboard': '',
    'Play': '',
}

default_symbol = ''

colors = {
    'session_line_session_name': '\033[32m',
    'window_name': '\033[34m',
    'window_line_session_name': '\033[38;5;242m',
}

cr = '\033[0m'   # reset style
ch = '\033[30m'  # hide foreground into background

fzf_ui_left_margin = 4
fzf_ui_gap = 10


class FZFFormatter:

  def __init__(self, snapshot):
    '''
    snapshot: {sid: tmux.Session}
    '''
    self.snapshot = snapshot
    self.fzf_ui_width =         \
        fzf_ui_left_margin +    \
        self.snapshot.w_width + \
        fzf_ui_gap +            \
        self.snapshot.s_width

  def fzf_lines(self):
    lines = []
    for session in self.snapshot.session_map.values():
      lines.append('\n' + self.session_line(session.id, session.name))

      for window in session.windows:
        lines.append(self.window_line(session.name, window.id, window.name))

    return '\n'.join(lines)

  def window_line(self, session_name, window_id, window_name):
    color1 = colors['window_name']
    part1 = f'{color1}{window_name}{cr}'
    part1_width = 5 + self.snapshot.w_width + 4  # 5 + 4 for ansi color sequence

    color2 = colors['window_line_session_name']
    part2 = f'{color2}{session_name}{cr}'

    return f'{window_id}\t{ch}⋅{cr} {part1:{part1_width}}{" ":{fzf_ui_gap}}{part2}'

  def session_line(self, session_id, session_name):
    symbol = symbols.get(session_name, default_symbol)
    color = colors['session_line_session_name']
    return f'{session_id}\t{symbol} {color}{session_name}{cr}'
