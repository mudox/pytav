# -*- coding: utf-8 -*-

import tav.settings as cfg


def test_tmux_section():
  assert cfg.tmux.serverPID is not None
