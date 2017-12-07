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
      - sname_max_width
      - wname_max_width
      - server_pid
      - window_count
      - live_session_count
      - dead_session_count
    '''
    self.all_sessions = []  # list of tmux.Session objects
    self.server_pid = tmux.get_server_pid()

    #
    # scan live sessions
    #

    window_info_tuples = tmux.list_all_windows()

    # get tmux server id

    self.live_sessions = []
    groups = groupby(window_info_tuples, lambda x: (x[0], x[1]))
    for (sid, sname), value in groups:
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      for _, _, wid, wname in value:
        session.windows.append(tmux.Window(id=wid, name=wname))

      self.live_sessions.append(session)

    self.sname_max_width = reduce(max, [len(t[3]) for t in window_info_tuples])
    self.wname_max_width = reduce(max, [len(t[1]) for t in window_info_tuples])

    self.live_session_count = len(self.live_sessions)
    window_counts = [len(s.windows) for s in self.live_sessions]
    self.window_count = sum(window_counts)
    self.all_sessions += self.live_sessions

    #
    # scan dead sessions
    #

    live_snames = [s.name for s in self.live_sessions]

    snames = [
        x.stem for x in settings.paths.sessions.glob('*')
        if not x.stem.startswith('.')]

    dead_snames = [n for n in snames if n not in live_snames]

    # update self.sname_max_width
    width = reduce(max, [len(n) for n in dead_snames])
    self.sname_max_width = max(self.sname_max_width, width)

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
    self.dead_session_count = len(self.dead_sessions)
