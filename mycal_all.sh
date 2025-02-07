#!/bin/sh
DIR="/Users/jon.stephan/temp/repos/gcaldisp"
tmux new-session -s "mycal" -d "tty-clock -stc"
tmux split-window -t mycal -v "$DIR/mycal_top.sh"
tmux split-window -t mycal -v "$DIR/mycal_bottom.sh"
tmux resize-pane -tmycal:0.0 -y 11
tmux resize-pane -tmycal:0.1 -y 35
tmux a -t mycal
