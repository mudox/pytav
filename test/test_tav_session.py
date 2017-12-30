# -*- coding: utf-8 -*-

from tav import settings as cfg
from tav.tmux import tavSession


def test():
  tavSession.swapYinYang(force=True)
  assert tavSession.isYinReady()
  assert tavSession.isYangReady()
  assert tavSession.ttyOf(cfg.tmux.yin.target) is not None
  assert tavSession.ttyOf(cfg.tmux.yang.target) is not None
