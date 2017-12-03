#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

import core
import settings

def enable(flag):
  settings.paths.update.write_text(flag and 'yes' or 'no')


def is_enabled() -> bool:
  if not settings.paths.update.exists():
    return True

  text = settings.paths.update.read_text()
  return (text == 'yes') and True or False


def run():
  if not is_enabled():
    print('disabled')
    return
  else:
    core.update()
    subprocess.run(['tmux', 'respawn-window', '-k', '-t', 'Tmux:Navigator'])
