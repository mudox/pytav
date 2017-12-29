#!/usr/bin/env bash
PS4="
🚩  "

set -euxo pipefail

cd "${HOME}/Develop/Python/tav"

yapf --recursive --parallel --in-place --verbose .
flake8 .
pip3 install --no-deps -U .
pytest -v .
tav restart
