#!/usr/bin/env bash

_fzf() {
  fzf                    \
    --exact              \
    --with-nth=2..       \
    --tiebreak=index     \
    --ansi               \
    --height=100%        \
    --margin=0
}

_target_lines() {
  declare -A _symbols
  _symbols[Configure]=
  _symbols[Update]=
  _symbols[Dashboard]=
  _symbols[Play]=

  session_lines=$(tmux list-sessions -F '#{session_id} #S')
  while read session_id session_name; do
    symbol="${_symbols[$session_name]:-}"
    printf "\n%s\t %s \n" "$session_id" "$symbol [38;5;16m$session_name[0m"
    window_lines=$(tmux list-windows -t "${session_id}" -F '#{window_id} #W')
    while read window_id window_name; do
      printf "%s\t -  %-32s%-20s\n" "$window_id" "[38;5;048m$window_name[0m" "[38;5;242m$session_name[0m"
    done <<< "$window_lines"
  done <<< "$session_lines"
}

_update() {
  local dst="$HOME/.local/share/tmux-choose-tree/tree" &>/dev/null
  mkdir -p "$(dirname "${dst}")"
  _target_lines > "${dst}"
}

_choose_tree() {
  target=$(_target_lines | _fzf | cut -f1)
  tmux switch-client -t "$target" &>/dev/null
}

_choose_tree
