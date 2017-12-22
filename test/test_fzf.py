# -*- coding: utf-8 -*-

from tav import tmux
from tav.fzf import FZFFormatter


def test_fzf_feed():
  snapshot = tmux.Snapshot()
  formatter = FZFFormatter(snapshot)
  feed = formatter.fzfFeed
  firstLine = feed.splitlines()[0]
  assert firstLine == '', \
      "first must be empty line, so that sending `c-u c-m` trigger a ui refresh"
