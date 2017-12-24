# -*- coding: utf-8 -*-

from tav.settings import cfg


def test_tmux_serverPID():
  assert cfg.tmux.serverPID is not None
