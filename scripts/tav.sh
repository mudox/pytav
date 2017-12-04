#!/usr/bin/env bash
set -euo pipefail

script_dir=$(dirname $(test -L "$0" && readlink -e "$0" || echo "$0"))
"${script_dir}/prepare_tmux_interface.sh" nokill &>/dev/null
tmux switch-client -t "Tav:Finder"
