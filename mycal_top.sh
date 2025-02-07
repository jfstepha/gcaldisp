while [ 1  ]
do
    gcalcli agenda --tsv --details calendar --calendar stephan > mycal.tsv
    clear
    python3 gcaldisp.py
    sleep 60
done
