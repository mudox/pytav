# -*- coding: utf-8 -*-

from tav.tmux import tavSession

def test():
  tavSession.refresh()
  assert tavSession.isReady()
  assert tavSession.getTavWindowTTY() is not None
