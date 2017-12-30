# -*- coding: utf-8 -*-

import logging

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import settings as cfg

logger = logging.getLogger(__name__)


class EventHandler(FileSystemEventHandler):

  def on_any_event(self, event):
    path = event.src_path
    if path.endswith('tav/tav.yml'):
      pass
    elif path.is_directory:
      pass


def startMonitoring():
  handler = EventHandler()
  observer = Observer()
  observer.schedule(handler, str(cfg.paths.userConfigDir), recursive=True)
  observer.start()

  handler = EventHandler()
  observer = Observer()
  observer.schedule(handler, str(cfg.paths.sessionsDir), recursive=True)
  observer.start()
