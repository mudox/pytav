# -*- coding: utf-8 -*-

from typing import NamedTuple


class Server(NamedTuple):
  sessions: list


class Window(NamedTuple):
  id: str
  name: str
  index: int

  def __eq__(self, rhs):
    if not isinstance(rhs, Window):
      return NotImplemented

    if self is rhs:
      return True

    return                         \
        self.id == rhs.id and      \
        self.name == rhs.name and  \
        self.index == rhs.index


class Session(NamedTuple):
  name: str
  loaded: bool
  id: str
  windows: list

  def __eq__(self, rhs):
    if not isinstance(rhs, Session):
      return NotImplemented

    if self is rhs:
      return True

    for a in ('id', 'loaded', 'name'):
      if getattr(self, a) != getattr(rhs, a):
        return False

    if len(self.windows) != len(rhs.windows):
      return False

    return self.windows == rhs.windows


class Pane(NamedTuple):
  tty: str
