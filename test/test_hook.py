#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav.tmux import hook


def test_hook_suppression():
  hook.disable('testing')
  assert not hook.isEnabled()

  hook.enable('testing')
  assert hook.isEnabled()
