#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

import core

out_dir = Path('~/.local/share/tav').expanduser()
out_dir.mkdir(parents=True, exist_ok=True)
fzf_feed_path = out_dir / 'fzf-feed'
width_path = out_dir / 'width'
update_path = out_dir / 'update'


def enable(flag):
  with open(str(update_path), 'w') as file:
    file.write(flag and 'yes' or 'no')


def is_enabled() -> bool:
  if not update_path.exists():
    return True

  with open(str(update_path)) as file:
    if file.read() == 'no':
      return False
    else:
      return True


def run():
  if not is_enabled():
    print('disabled')
    return
  else:
    core.update()
    subprocess.run(['tmux', 'respawn-window', '-k', '-t', 'Tmux:Navigator'])
