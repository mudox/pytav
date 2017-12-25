#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav.tmux.hook import *


def test_hook_suppression():
  disable()
  assert not isEnabled()

  enable()
  assert isEnabled()

