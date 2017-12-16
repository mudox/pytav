#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav import tmux


def test_listAllWindows():
  assert tmux.listAllWindows() != ''
