#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from itertools import groupby

from .. import settings, tmux


class Snapshot:

  def __init__(self):
    '''
      take a snapshot, provides following atrributes
      - allSessions
      - liveSessions
      - deadSessions
      - sessionNameMaxWidth
      - windowNameMaxWidth
      - serverPID
      - windowCount
      - liveSessionCount
      - deadSessionCount
    '''
    self.allSessions = []  # list of tmux.Session objects
    self.serverPID = settings.tmux.serverPID

    #
    # scan live sessions
    #

    infoTuples = tmux.dumpInfo()

    # get tmux server id

    self.liveSessions = []
    # filter out tav session
    infoTuples = list(filter(lambda x: x[1] != settings.tmux.tavSessionName, infoTuples))
    groups = groupby(infoTuples, lambda x: (x[0], x[1]))
    for (sid, sname), value in groups:
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      for _, _, wid, wname, windex in value:
        session.windows.append(tmux.Window(wid, wname, windex))

      self.liveSessions.append(session)

    self.sessionNameMaxWidth = reduce(
        max, [len(t[1]) for t in infoTuples])
    self.windowNameMaxWidth = reduce(
        max, [len(t[3]) for t in infoTuples])

    self.liveSessionCount = len(self.liveSessions)
    windowCounts = [len(s.windows) for s in self.liveSessions]
    self.windowCount = sum(windowCounts)
    self.allSessions += self.liveSessions

    #
    # scan dead sessions
    #

    live_snames = [s.name for s in self.liveSessions]

    snames = [
        x.stem
        for x in settings.paths.sessions.glob('*')
        if not x.stem.startswith('.')
    ]

    dead_snames = [n for n in snames if n not in live_snames]

    if len(dead_snames) == 0:
      self.deadSessions = None
      self.deadSessionCount = 0
      return

    # update self.sessionNameMaxWidth
    width = reduce(max, [len(n) for n in dead_snames])
    self.sessionNameMaxWidth = max(self.sessionNameMaxWidth, width)

    self.deadSessions = []
    for name in dead_snames:
      session = tmux.Session(
          id='<dead>',
          name=name,
          loaded=False,
          windows=None)
      self.deadSessions.append(session)

    self.allSessions += self.deadSessions
    self.deadSessionCount = len(self.deadSessions)
