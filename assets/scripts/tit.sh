#!/usr/bin/env bash
set -euo pipefail

PS4="
🚩  "
set -euxo pipefail

root="${HOME}/Develop/Python/tav"
pip3 install --no-deps -U "${root}"
pytest -v "${root}"
tmux send-keys -t 'Tav-Project:Server.2' c-c c-c ' tavs restart' c-m
sleep 1
tavs event after-install
