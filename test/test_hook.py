#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav.tmux.hook import *


def test_hook_suppression():
  disable('testing')
  assert not isEnabled()

  enable('testing')
  assert isEnabled()
