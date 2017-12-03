#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path


class paths:
  install = Path(__file__)
  scripts = install / 'scripts'

  data = Path('~/.local/share/tav').expanduser()

  fzf_feed = data / 'fzf-feed'
  width = data / 'fzf-width'
  update = data / 'update'
  sessions = data / 'sessions'


paths.data.mkdir(parents=True, exist_ok=True)

reenable_hook_interval = 4


class colors:
  # TODO: migrate colors here
  pass


class symbols:
  # TODO: migrate symbols here
  pass
