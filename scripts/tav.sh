#!/usr/bin/env bash
set -euo pipefail

script_dir=$(dirname $(test -L "$0" && readlink -e "$0" || echo "$0"))

session_name='Tmux'
window_name='Navigator'
window_target="${session_name}:${window_name}"

cmd="${script_dir}/tav.py serve"

if ! tmux has-session -t "${session_name}" &>/dev/null; then
  tmux new-session -s "${session_name}" -n "${window_name}" -d "${cmd}"
fi

tmux switch-client -t "${window_target}"
