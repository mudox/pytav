#!/usr/bin/env bash

kill=${1:-kill}

is_tmux_interface_prepared() {
  tmux list-panes -t 'Tav:Finder' &>/dev/null
}

session_name='Tav'

create_session() {

  # tty size
  if [[ -n "$TMUX" ]]; then
    tty_width="$(tmux list-clients -t '.' -F '#{client_width}')"
    tty_height="$(tmux list-clients -t '.' -F '#{client_height}')"
  else
    tty_height=$(tput lines)
    tty_width=$(tput cols)
  fi

  # disable hook updating temporarily
  date '+%s' > "${HOME}/.local/share/tav/update"
  trap 'echo "-1" > "${HOME}/.local/share/tav/update"' EXIT

  #
  # window: Finder
  #

  window_name='Finder'
  window="${session_name}:${window_name}"
  tmux new-session       \
    -s "${session_name}" \
    -n "${window_name}"  \
    -x "${tty_width}"    \
    -y "${tty_height}"   \
    -d                   \
    tav serve

  # set background transparent to speed up rendering
  tmux select-pane -t "${window}.1" -P 'bg=black'

  # hide status bar, make it full screen like
  tmux set -t "${session_name}" status off

  #
  # window: Log
  #

  window_name='Log'
  window="${session_name}:${window_name}"
  tmux new-window              \
    -a                         \
    -t "${session_name}:{end}" \
    -n "${window_name}"        \
    -d                         \
    sh

  # disable the window
  tmux select-pane -t "${window}.1" -d
}

if [[ ${kill} == 'kill' ]]; then
  tmux kill-session -t "${session_name}" &>/dev/null
  create_session
else
  if ! is_tmux_interface_prepared; then
    create_session
  fi
fi

