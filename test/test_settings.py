#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav import settings


def test_tmux_serverPID():
  assert settings.tmux.serverPID is not None


def test_logTTY():
  assert settings.tmux.logTTY.exists()
