#!/usr/bin/env bash
set -euo pipefail

source ~/Git/dot-files/bash/lib/jack

tput civis
trap 'tput cnorm' EXIT

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
# window: Edit
#
jackProgress 'Creating window [Edit] ...'

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
v py **/*.{py,sh} .exrc .tmux-session.sh
'
tmux split-window  \
  -t "${window}.1" \
  -h               \
  -c "${root}"
tmux select-pane -t "${window}.1"

sleep 0.2

#
# window: Server
#

jackProgress 'Creating window [Server] ...'

root="${HOME}/.local/share/tav"
window_name='Server'
window="${session_name}:${window_name}"
tmux new-window              \
  -a                         \
  -t "${session_name}:{end}" \
  -n "${window_name}"        \
  -c "${root}"               \
  -d                         \
  'tput civis; tail -f log/server.log'

tmux select-pane -t "${window}.1" -d

#
# pane: Server.2
# to the right
# run command
#

root="${HOME}/.local/share/tav"
tmux split-window  \
  -t "${window}.1" \
  -h               \
  -l 60            \
  -c "${root}"

tmux select-pane -t "${window}.2"

sleep 0.2

#
# window: Interface
#

jackProgress 'Creating window [Interface] ...'

root="${HOME}/.local/share/tav"
window_name='Interface'
window="${session_name}:${window_name}"
tmux new-window              \
  -a                         \
  -t "${session_name}:{end}" \
  -n "${window_name}"        \
  -c "${root}"               \
  -d                         \
  'tput civis; tail -f log/interface.log'

tmux select-pane -t "${window}.1" -d

#
# pane: Interface.2
# at the bottom right corner
# for running testing commands
#

root="${HOME}/Develop/Python/tav"
tmux split-window  \
  -t "${window}.1" \
  -h               \
  -l 60            \
  -c "${root}"

tmux select-pane -t "${window}.2"

sleep 0.2

#
# window: Log
#

jackProgress 'Creating window [Log] ...'

root="${HOME}/.local/share/tav"
window_name='Log'
window="${session_name}:${window_name}"
tmux new-window              \
  -a                         \
  -t "${session_name}:{end}" \
  -n "${window_name}"        \
  -c "${root}"               \
  -d                         \
  'tput civis; tail -f log/tav.log'

tmux select-pane -t "${window}.1" -d

#
# pane: Log.2
# at the bottom right corner
# for running testing commands
#

root="${HOME}/Develop/Python/tav"
tmux split-window  \
  -t "${window}.1" \
  -h               \
  -l 60            \
  -c "${root}"

tmux select-pane -t "${window}.2"

sleep 0.2

jackEndProgress

tmux select-window -t "${session_name}:1.1"
echo "[${session_name}]"
tmux list-window -t "${session_name}" -F ' - #W'
