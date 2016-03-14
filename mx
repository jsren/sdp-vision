#!/bin/bash

if [[ $# -eq 0 ]]; then
  while read; do
    tmux send-keys -t matlab "$REPLY"$'\n'
  done
else
  tmux send-keys -t matlab "$@"$'\n'
fi
