# -*- coding: utf-8 -*-

import logging
import subprocess as sp
from textwrap import indent

logger = logging.getLogger(__name__)

# logger.setLevel(logging.WARNING)


def check(cmdstr):
  return run(cmdstr).returncode == 0


def system(cmdstr):
  # left unchanged (connect to controlling terminal)
  run(cmdstr, stdout=None)


def getStdout(cmdstr):
  p = run(cmdstr, stdout=sp.PIPE)
  if p.returncode != 0:
    logger.warning(f'o:output:\nNone')
    return None
  else:
    text = p.stdout.decode()
    logger.debug(f'o:output:\n{text}')
    return text


def run(cmdstr, stdout=sp.DEVNULL, trace=True):
  """Execute the command line using `subprocess.run`.

  The stdout's redirection is controlled by the argument `stdout`, which is
    `DEVNULL` by defaults.
  The stderr is captured.

  Check the return code, log out content captured from stderr if is not 0.

  Args:
    cmstr (str): Command line string to run like in shell which can contain
      comments.
    stdout (number of file object): Control the redireciton of the stdout.

  Returns:
    The process object returned from `subprocess.run`.
  """

  # logger.debug(f'cmd: {cmdstr.strip()}')
  cmdstr = f'set -x\n{cmdstr}'

  p = sp.run(cmdstr, shell=True, stderr=sp.PIPE, stdout=stdout)

  text = p.stderr.decode().strip()
  if p.returncode != 0:
    logger.error(f'''m:
        failed with error code: {p.returncode}
        {indent(text, '  ')}
    ''')
  else:
    logger.debug(f'succeed to execute:\n{text}')

  return p
