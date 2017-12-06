#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from itertools import groupby

import settings
import tmux


class Snapshot:

  def __init__(self):
    '''
      take a snapshot, provides following atrributes
      - all_sessions
      - live_sessions
      - dead_sessions
      - s_width
      - w_width
      - srv_pid
    '''
    self.all_sessions = []  # list of tmux.Session objects

    #
    # scan live sessions
    #

    fields = tmux.list_all_windows()

    # get tmux server id
    pid = fields[0][4]
    fields = [t[:-1] for t in fields]

    self.live_sessions = []
    groups = groupby(fields, lambda x: (x[0], x[1]))
    for (sid, sname), value in groups:
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      for _, _, wid, wname in value:
        session.windows.append(tmux.Window(id=wid, name=wname))

      self.live_sessions.append(session)

    self.s_width = reduce(max, [len(t[3]) for t in fields])
    self.w_width = reduce(max, [len(t[1]) for t in fields])

    self.all_sessions += self.live_sessions

    #
    # scan dead sessions
    #

    live_snames = [s.name for s in self.live_sessions]

    snames = [
        x.stem for x in settings.paths.sessions.glob('*')
        if not x.stem.startswith('.')]

    dead_snames = [n for n in snames if n not in live_snames]

    # update self.s_width
    width = reduce(max, [len(n) for n in dead_snames])
    self.s_width = max(self.s_width, width)

    self.dead_sessions = []
    for name in dead_snames:
      session = tmux.Session(
          id='<dead>',
          name=name,
          loaded=False,
          windows=None
      )
      self.dead_sessions.append(session)

    self.all_sessions += self.dead_sessions
