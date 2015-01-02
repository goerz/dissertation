#tmux new-session -s diss


tmux send-keys -t diss:1 ":qa!" C-m
tmux kill-window -t diss:1

tmux send-keys -t diss:2 ":qa!" C-m
tmux kill-window -t diss:2

tmux send-keys -t diss:3 ":qa!" C-m
tmux kill-window -t diss:3

tmux send-keys -t diss:4 ":qa!" C-m
tmux kill-window -t diss:4

tmux send-keys -t diss:5 ":qa!" C-m
tmux kill-window -t diss:5

tmux send-keys -t diss:6 ":qa!" C-m
tmux kill-window -t diss:6

tmux send-keys -t diss:7 ":qa!" C-m
tmux kill-window -t diss:7

tmux send-keys -t diss:8 ":qa!" C-m
tmux kill-window -t diss:8

tmux select-window -t diss:0
