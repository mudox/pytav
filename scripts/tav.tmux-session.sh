#!/usr/bin/env bash
set -euo pipefail

source ~/Git/dot-files/bash/lib/jack

# kill session if exists
session_name='Tav'
if tmux has-session -t ${session_name} &>/dev/null; then
  if [[ ${1:-kill} == 'nokill' ]]; then
    jackInfo "session [${session_name}] already exisits, abort!"
    exit 0
  fi

  jackWarn "session [${session_name}] already exisits, kill it!"
  tmux kill-session -t "${session_name}"
fi

# tty size
set +u
if [[ -n "$TMUX" ]]; then
  tty_width="$(tmux list-clients -t '.' -F '#{client_width}')"
  tty_height="$(tmux list-clients -t '.' -F '#{client_height}')"
else
  tty_width=$(tput lines)
  tty_height=$(tput cols)
fi
set -u


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
