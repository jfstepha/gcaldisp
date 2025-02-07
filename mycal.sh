while [ 1  ]
do
    gcalcli agenda --tsv --details calendar --calendar stephan > mycal.tsv
    clear
    #date +"%H : %M" | figlet -f banner
    python3 gcaldisp.py
    gcalcli agenda 8:00 18:00 --details conference
    sleep 60
done
