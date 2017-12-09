#!/usr/bin/env bash
set -euo pipefail

s_dir=$(dirname $(test -L "$0" && readlink -e "$0" || echo "$0"))

for event in window-linked window-renamed window-unlinked; do
  tmux set-hook -g "${event}" "run-shell '${s_dir}/../tav.py hook ${event}'"
done
