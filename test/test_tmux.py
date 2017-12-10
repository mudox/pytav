#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tav import settings, tmux


def test_serverPID():
  assert settings.serverPID is not None


def test_logTTY():
  assert settings.paths.logTTY is not None
  assert settings.paths.logTTY.exists()
