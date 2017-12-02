#!/usr/bin/env bash
set -euo pipefail

session_name='Tmux'
window_name='Navigator'
window_target="${session_name}:${window_name}"

cmd='ct interface'

if tmux has-session -t "${session_name}" &>/dev/null; then
  tmux respawn-window -k -t "${window_target}"
else
  tmux new-session -s "${session_name}" -n "${window_name}" -d "${cmd}"
fi

tmux switch-client -t "${window_target}"
