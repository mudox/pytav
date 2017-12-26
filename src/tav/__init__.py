import logging

from jaclog import jaclog

from sys import argv

if argv[1] == 'server':
  jaclog.configure(appName='tav', fileName='server.log', compact=True)
elif argv[1] == 'interface':
  jaclog.configure(appName='tav', fileName='interface.log', compact=True)
else:
  jaclog.configure(appName='tav', compact=True)

logging.getLogger('tav.tmux.agent').setLevel(logging.WARNING)
logging.getLogger('tav.fzf').setLevel(logging.WARNING)
