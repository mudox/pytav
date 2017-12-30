set -exuo pipefail
PS4='
🎾  '
name="Test${RANDOM}"
tmux new-session -d -s "${name}"
sleep 2
tmux kill-session -t "${name}"
