#tmux new-session -s diss

#tmux new-window -t diss:0
tmux rename-window -t diss:0 "main"

tmux new-window -t diss:1
tmux rename-window -t diss:1 "intro"
tmux send-keys -t diss:1 "vim chapters/intro.tex" C-m

tmux new-window -t diss:2
tmux rename-window -t diss:2 "quantum"
tmux send-keys -t diss:2 "vim chapters/quantum.tex" C-m

tmux new-window -t diss:3
tmux rename-window -t diss:3 "numerics"
tmux send-keys -t diss:3 "vim chapters/numerics.tex" C-m

tmux new-window -t diss:4
tmux rename-window -t diss:4 "robust"
tmux send-keys -t diss:4 "vim chapters/robust.tex" C-m

tmux new-window -t diss:5
tmux rename-window -t diss:5 "transmon"
tmux send-keys -t diss:5 "vim chapters/transmon.tex" C-m

tmux new-window -t diss:6
tmux rename-window -t diss:6 "pe"
tmux send-keys -t diss:6 "vim chapters/pe.tex" C-m

tmux new-window -t diss:7
tmux rename-window -t diss:7 "3states"
tmux send-keys -t diss:7 "vim chapters/3states.tex" C-m

tmux new-window -t diss:8
tmux rename-window -t diss:8 "outlook"
tmux send-keys -t diss:8 "vim chapters/outlook.tex" C-m

tmux select-window -t diss:0
