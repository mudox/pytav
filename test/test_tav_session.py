# -*- coding: utf-8 -*-

from tav.tmux import tavSession

def test():
  tavSession.create()
  assert tavSession.isReady()
  assert tavSession.getFrontWindowTTY() is not None
