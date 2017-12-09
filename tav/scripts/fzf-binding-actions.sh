#!/usr/bin/env bash
set -euo pipefail

# parse $*

echo $* | IFS='	' read tag name
