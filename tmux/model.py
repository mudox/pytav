#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NamedTuple


class Window(NamedTuple):
  id: str
  name: str


class Session(NamedTuple):
  name: str
  loaded: bool
  id: str
  windows: list
