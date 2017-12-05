#!/usr/bin/env bash
set -euo pipefail

source ~/Git/dot-files/bash/lib/jack

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

# kill session if exists
session_name='Tav-Project'
if tmux has-session -t ${session_name} &>/dev/null; then
  jackWarn "session [${session_name}] already exists, kill it!"
  tmux kill-session -t "${session_name}"
fi

#
# window: Editor
#

root="${HOME}/Develop/Python/tav"
window_name='Edit'
window="${session_name}:${window_name}"
tmux new-session       \
  -s "${session_name}" \
  -n "${window_name}"  \
  -x "${tty_width}"    \
  -y "${tty_height}"   \
  -c "${root}"         \
  -d
tmux send-keys -t "${window}.1" '
v py **/*.{py,sh} .*
'
tmux split-window  \
  -t "${window}.1" \
  -h               \
  -c "${root}"
tmux select-pane -t "${window}.1"


tmux select-window -t "${session_name}:1.1"
echo "[${session_name}]"
tmux list-window -t "${session_name}" -F ' - #W'
