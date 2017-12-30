# -*- coding: utf-8 -*-

from functools import reduce
from itertools import groupby

from .. import settings as cfg
from .. import tmux


class Snapshot:

  def __init__(self):
    '''
      Take a snapshot, provides following atrributes

      + Tmux model objects
        - allSessions
        - liveSessions
        - deadSessions

      + Width statistics
        - sessionNameMaxWidth
        - windowNameMaxWidth

      + Tmux server info
        - serverPID

      + Counts
        - windowCount
        - liveSessionCount
        - deadSessionCount

      + Current tty size
        - ttyWidth
        - ttyHeight
    '''
    self.allSessions = []  # list of tmux.Session objects
    self.serverPID = cfg.tmux.serverPID

    #
    # scan live sessions
    #

    infoList = tmux.dump()
    self.ttyWidth = int(infoList[0].wwidth)
    self.ttyHeight = int(infoList[0].wheight)

    # get tmux server id

    self.liveSessions = []

    # filter out tav session
    infoList = list(
        filter(
            lambda x: x.sname not in (cfg.tmux.yin.sname, cfg.tmux.yang.sname),
            infoList,
        ))

    # group by sessions ID
    groups = groupby(infoList, lambda x: (x.sid, x.sname))
    for (sid, sname), infos in groups:
      session = tmux.Session(id=sid, name=sname, loaded=True, windows=[])
      for info in infos:
        session.windows.append(tmux.Window(info.wid, info.wname, info.windex))

      self.liveSessions.append(session)

    self.sessionNameMaxWidth = reduce(max,
                                      [len(info.sname) for info in infoList])
    self.windowNameMaxWidth = reduce(max,
                                     [len(info.wname) for info in infoList])

    self.liveSessionCount = len(self.liveSessions)
    windowCounts = [len(s.windows) for s in self.liveSessions]
    self.windowCount = sum(windowCounts)
    self.allSessions += self.liveSessions

    #
    # scan dead sessions
    #

    live_snames = [s.name for s in self.liveSessions]

    snames = [
        x.stem for x in cfg.paths.sessionsDir.glob('*')
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
          id='<dead>', name=name, loaded=False, windows=None)
      self.deadSessions.append(session)

    self.allSessions += self.deadSessions
    self.deadSessionCount = len(self.deadSessions)
