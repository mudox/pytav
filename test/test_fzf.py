# -*- coding: utf-8 -*-

import tav.settings as cfg
from tav import tmux
from tav.fzf import FZFFormatter


def test_layout():
  snapshot = tmux.Snapshot()
  formatter = FZFFormatter(snapshot)
  feed = formatter.fzfFeed
  firstLine = feed.splitlines()[0]
  assert firstLine == '', \
      "first must be empty line, so that sending `c-u c-m` trigger a ui refresh"

  for lvl in range(5):
    cfg.fzf.layoutLevel = lvl
    formatter = FZFFormatter(snapshot)
    lineCount = len(formatter.fzfFeed.strip().splitlines())
    height = formatter._height(lvl)
    lineCount += 3 + 4 + 2
    assert lineCount == height
