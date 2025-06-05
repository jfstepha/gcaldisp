import shutil
import argparse
import datetime

# "stephan" matches both jon.stephan@sifive.com and Stephan Oberlin Merged
# gcalcli agenda --tsv --details calendar --calendar stephan > mycal.tsv

NC='\033[0m'
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
# Background
REDBG='\033[0;41m'
PURPLEBG='\033[0;45m'
BLUEBG='\033[0;44m'

def strtime_to_int(strtime):
#    print(f"splitting {strtime}")
    h,m = strtime.split(":")
    return(int(h)*60+int(m))

def int_to_strtime(inttime):
    h,m = divmod(inttime, 60)
    if h >12:
        h=h-12
        ampm="p"
    else:
        ampm='a'
    return(f"{h:02}:{m:02}{ampm}")

def isin_active_col_names(active_cols, name):
    retval = False
    for item in active_cols:
        if item['name'] == name:
            retval = True
    return retval

def strip_colors( instring):
    outstring = instring.replace(REDBG,"").replace(PURPLEBG,"").replace(NC,"")
    return outstring


def get_active_col_index(active_cols, name):
    retval = -1
    i=0
    for item in active_cols:
        # print (f"item={item}")
        if item['name'] == name:
            retval = i
        i += 1
    return retval

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--header_row',action='store_true')
    parser.add_argument('-s', '--start_time',default = "07:00")
    parser.add_argument('-t', '--stop_time',default = "22:00")
    parser.add_argument('-e', '--step_time',default = 30)
    parser.add_argument('-w', '--width', type=int, help='Display width in columns. Defaults to terminal width if not specified.')
    parser.add_argument('-i', '--input_filename', default="mycal.tsv")
    
    args = parser.parse_args()
    header_row = args.header_row
    start_time = args.start_time
    stop_time = args.stop_time
    step = int(args.step_time)



    f = open(args.input_filename)
    i=0
    cal = []
    if header_row == False:
       header=['start_date','start_time','end_date','end_time','title','calendar']
    for line in f:
        l = line.replace("\n","").split('\t')

        if i == 0 and header_row:
            header = l
        else:
            row = {}
            for c in range(len(l)):
                row[header[c]] = l[c]

            cal.append(row)
        #print(f"Line:{i}:{l}")
        i+=1


    print("processing calendar")
    dates = []
    for i in range(len(cal)):
        if len(cal[i]['start_time']) == 5:
            # print(f"{i}: {cal[i]['start_time']}")
            if(cal[i]['start_date'] not in dates):
                dates.append(cal[i]['start_date'])
            cal[i]['start_time_int'] = strtime_to_int(cal[i]['start_time'])
            cal[i]['end_time_int'] = strtime_to_int(cal[i]['end_time'])
        else:
            cal[i]['start_time_int'] = 0
            cal[i]['end_time_int'] = 0

    # print(f"calendar={cal}")



    term_columns = args.width if args.width else shutil.get_terminal_size().columns
    daywidth = int(term_columns / len(dates)) - 5
    # print(f"daywidth={daywidth}")

    rowstr="      "
    for date in dates:
        rowstr += f"| {date}"+" "*(daywidth-len(date)-1) 
    print(rowstr)

    rowstr="      "
    for date in dates:
        weekday=datetime.date.fromisoformat(date).strftime("%A")
        rowstr += f"| {weekday}" + " " * (daywidth-len(weekday)-1)
    print(rowstr)

    rowstr="          "
    for date in dates:
        rowstr += "=" * (daywidth)
    print(rowstr)

    active_columns={}
    for date in dates:
        active_columns[date] = []

    for t in range( strtime_to_int(start_time), strtime_to_int(stop_time), step):
       # print(f"dates:{dates}")
        rowstr=""
        for date in dates:
            busy=False
            daystr=""
            for i in range(len(cal)):
                # if there are multiple items with the same name at the same time on different days, then duplicates get dropped
                # this is a workaround, but #TODO to change to only when we need it.  Probably add an instance_name and do seaches
                # based on that 
                item_name = cal[i]['title'] + " "*500 + str(i)
                if cal[i]['start_date'] == date and (cal[i]['start_time_int'] <= t) and (cal[i]['end_time_int'] > t):
                        # print(f"event is now:{cal[i]['title']}")
                        busy= True
                        if cal[i]['calendar'] == "Stephan Oberlin Merged":
                            color = PURPLEBG
                        else:
                            color = REDBG
                        if isin_active_col_names(active_columns[date], item_name):
                            c = get_active_col_index(active_columns[date], item_name)
                            active_columns[date][c]['firstrow'] = False
                        else:
                            active_columns[date].append({'name':item_name, 'color':color, 'firstrow':True, 'active':True})
                else:
                    if isin_active_col_names(active_columns[date], item_name):
                        c = get_active_col_index(active_columns[date], item_name)
                        active_columns[date][c]['active'] = False
            if busy:
                if len(active_columns[date]) == 0:
                    colwidth = daywidth
                else:
                    colwidth = int(daywidth / len(active_columns[date]))
                for event in active_columns[date]:
                    event_name = event['name']
                    color = event['color']
                    if event['active'] == False:
                        daystr += f"{NC}" + ' ' * colwidth
                    elif event['firstrow'] == False:
                        if get_active_col_index(active_columns[date], event_name) == 0:
                            daystr += f"{color}" + ' .' + ' ' * (colwidth-2)
                        else:
                            daystr += f"{NC}|{color}" + ' .' + ' ' * (colwidth-3)
                    else:
                        if get_active_col_index(active_columns[date], event_name) == 0:
                            daystr += f"{color}{event_name[:colwidth]}" + " " * (colwidth - len(event_name[:colwidth])) + f"{NC}"
                        else:
                            daystr += f"{NC}|{color}{event_name[:(colwidth-1)]}" + " " * (colwidth - len(event_name[:(colwidth-1)])-1)                    
                rowstr += f"{daystr}" + " " * ( daywidth - len(strip_colors(daystr) ) ) +  f"{NC}│"
            else:
                rowstr += " " * daywidth + "│"
                active_columns[date] = []
        now_t = datetime.datetime.now()
        now = now_t.hour * 60 + now_t.minute
        if now >= t and now < t + step:
            rowstr = rowstr.replace("  ",f"{GREEN}--")
            color=BLUEBG
        else:
            color=NC
        print( f"{color}{int_to_strtime(t)}{NC} {rowstr}" )

if __name__ == '__main__':
        main()  # next section explains the use of sys.exit
