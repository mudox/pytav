#!/usr/bin/env bash
set -euo pipefail

root="${HOME}/Develop/Python/tav"
pip3 install --no-deps -U "${root}" && \
  pytest -v "${root}" &&               \
  tav cc -f &&                         \
  tav hook window-linked
