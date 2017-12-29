# -*- coding: utf-8 -*-

import logging
from pathlib import Path

# from watchdog.events import RegexMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# from . import settings as cfg

logger = logging.getLogger(__name__)


class EventHandler(FileSystemEventHandler):

  def on_any_event(self, event):
    logger.info(f'''m:
        type: {event.event_type}
        path: {event.src_path}
    ''')


def startMonitoring():
  handler = EventHandler()
  observer = Observer()
  observer.schedule(
      handler, Path('~/.config/tav/').expanduser(), recursive=True)
  observer.start()
