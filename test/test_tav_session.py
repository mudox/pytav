# -*- coding: utf-8 -*-

from tav.tmux import tavSession


def test():
  tavSession.refresh(recreate=True)
  assert tavSession.isReady()
  assert tavSession.getTavWindowTTY() is not None
