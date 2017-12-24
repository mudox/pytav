#!/usr/bin/env bash
set -euo pipefail

PS4="
🚩  "
set -x

root="${HOME}/Develop/Python/tav"
pip3 install --no-deps -U "${root}" && \
  pytest -v "${root}" &&               \
  tav cc -f &&                         \
  tav hook window-linked
