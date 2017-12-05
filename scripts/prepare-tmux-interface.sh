#!/usr/bin/env bash
set -euo pipefail

is_tmux_interface_prepared() {
  cmd=$(tmux list-panes -t 'Tav:Finder.1' -F '#{pane_current_command}' || return 1 )
  [[ $cmd == 'Python' ]] || return 1
  tmux list-panes -t 'Tav:Log.1' &>/dev/null || return 2
}

# kill session if exists
session_name='Tav'
if is_tmux_interface_prepared; then
  echo -n "Tav tmux interface seems healthy. "

  if [[ ${1:-nokill} == 'nokill' ]]; then
    echo "Abort!"
    exit 0
  fi

  echo "Kill and recreate!"
  tmux kill-session -t "${session_name}"
else
  echo 'Tav tmux interface is not found'
fi

# tty size
set +u
if [[ -n "$TMUX" ]]; then
  tty_width="$(tmux list-clients -t '.' -F '#{client_width}')"
  tty_height="$(tmux list-clients -t '.' -F '#{client_height}')"
else
  tty_height=$(tput lines)
  tty_width=$(tput cols)
fi
set -u


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

tmux send-keys -t "${window}" '
tput civis
PS1=
clear
'
tmux select-pane -t "${window}" -d
