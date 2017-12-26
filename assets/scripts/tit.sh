#!/usr/bin/env bash
set -euo pipefail

PS4="
🚩  "
set -x

root="${HOME}/Develop/Python/tav"
pip3 install --no-deps -U "${root}" &&                                 \
  pytest -v "${root}" &&                                               \
  tmux send-keys -t 'Tav-Project:Server.2' c-c c-c 'tavs start' c-m && \
  tav cc -f &&                                                         \
  tavs event after-install
