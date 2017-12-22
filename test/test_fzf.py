# -*- coding: utf-8 -*-

from tav import settings, tmux
from tav.fzf import FZFFormatter


def test_fzf_feed():
  snapshot = tmux.Snapshot()
  formatter = FZFFormatter(snapshot)
  feed = formatter.fzfFeed
  firstLine = feed.splitlines()[0]
  assert firstLine == '', \
      "first must be empty line, so that sending `c-u c-m` trigger a ui refresh"

  for lvl in range(5):
    settings.fzf.layoutLevel = lvl
    formatter = FZFFormatter(snapshot)
    lineCount = len(formatter.fzfFeed.splitlines())
    height = formatter._height(lvl)
    height -= (3 + 1 + settings.fzf.yMargin * 2)
    # assert lineCount == height
