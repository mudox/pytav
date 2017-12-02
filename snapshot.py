#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shlex
import subprocess
import shutil

default_symbol = ''

symbols = {
    'Configure': '',
    'Update': '',
    'Dashboard': '',
    'Play': '',
}

colors = {
    'session_line_session_name': '\033[32m',
    'window_name': '\033[34m',
    'window_line_session_name': '\033[38;5;242m',
}

cr = '\033[0m'   # reset style
ch = '\033[30m'  # hide foreground into background

list_sessions_cmd = shlex.split('''
  tmux
  list-sessions
  -F
  '#{session_id}:#{session_name}'
''', comments=True)

list_windows_cmd = shlex.split('''
  tmux
  list-windows
  -F
  '#{window_id}:#{window_name}'
  -t
''', comments=True)


class TmuxSnapshot:

  def __init__(self):
    snapshot = {}
    w_width = 0  # max window name width
    s_width = 0  # max session name width

    p = subprocess.run(list_sessions_cmd, stdout=subprocess.PIPE)
    s_lines = p.stdout.decode().splitlines()

    for s_line in s_lines:
      s_id, s_name = s_line.split(':')
      snapshot[(s_id, s_name)] = []  # list of (w_id, w_name)

      s_width = max(s_width, len(s_name))

      cmd = list_windows_cmd + [s_id]
      p = subprocess.run(cmd, stdout=subprocess.PIPE)
      w_lines = p.stdout.decode().splitlines()

      for w_line in w_lines:
        w_id, w_name = w_line.split(':')
        snapshot[(s_id, s_name)].append((w_id, w_name))

        w_width = max(w_width, len(w_name))

    # widths
    t_width, t_height = shutil.get_terminal_size()

    self.s_width = s_width
    self.w_width = w_width

    prefix_width = 4
    self.gap = 10

    self.width = prefix_width + w_width + s_width + self.gap
    self.snapshot = snapshot

  def session_line(self, session_id, session_name):
    symbol = symbols.get(session_name, default_symbol)
    color = colors['session_line_session_name']
    return f'{session_id}\t{symbol} {color}{session_name}{cr}'

  def window_line(self, session_name, window_id, window_name):
    color1 = colors['window_name']
    part1 = f'{color1}{window_name}{cr}'
    part1_width = 5 + self.w_width + 4  # 5 + 4 for ansi color sequence

    color2 = colors['window_line_session_name']
    part2 = f'{color2}{session_name}{cr}'

    return f'{window_id}\t{ch}⋅{cr} {part1:{part1_width}}{" ":{self.gap}}{part2}'

  def fzf_lines(self):
    lines = []
    for (s_id, s_name), value in self.snapshot.items():
      lines.append('\n' + self.session_line(s_id, s_name))
      for w_id, w_name in value:
        lines.append(self.window_line(s_name, w_id, w_name))

    return '\n'.join(lines)

  # def update_choose(self):
    # self.update()
    # self.choose()

  # def master(self):
    # pass


if __name__ == "__main__":
  # main()
  TmuxSnapshot().update()
