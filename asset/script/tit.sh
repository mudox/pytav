#!/usr/bin/env bash
PS4="
🚩  "

set -euxo pipefail

cd "${HOME}/Develop/Python/tav"

isort --atomic --recursive .
yapf --recursive --parallel --in-place .
flake8 .
pip3 install --no-deps -U .
pytest -v .
tav restart
