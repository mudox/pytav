#!/usr/bin/env bash

if [[ $1 == '-f' || $1 == '--force' ]]; then
  force='yes'
else
  force='no'
fi

sessionName='Tav'

isTavSessionReady() {
  out="$(tmux list-panes -t 'Tav:Finder' -F '#{pane_current_command}' 2>/dev/null)"
  if [[ $out == 'Python' ]]; then
    return 0
  else
    return 1
  fi
}

createTavSession() {
  tmux kill-session -t "${sessionName}" &>/dev/null

  # tty size
  if [[ -n "$TMUX" ]]; then
    ttyWidth="$(tmux list-clients -t '.' -F '#{client_width}')"
    ttyHeight="$(tmux list-clients -t '.' -F '#{client_height}')"
  else
    ttyHeight=$(tput lines)
    ttyWidth=$(tput cols)
  fi

  #
  # window: Finder
  #

  windowName='Finder'
  window="${sessionName}:${windowName}"
  tmux new-session      \
    -s "${sessionName}" \
    -n "${windowName}"  \
    -x "${ttyWidth}"    \
    -y "${ttyHeight}"   \
    -d                  \
    tav serve

  # hide status bar, make it full screen like
  tmux set -t "${sessionName}" status off
}

if [[ ${force} == 'yes' || ! isTavSessionReady ]]; then
  createTavSession
fi
