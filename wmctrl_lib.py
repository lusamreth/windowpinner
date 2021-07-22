import subprocess
import traceback
import os.path
import time

# execute command
def bashrun(cmd,stillContine=False):
    sp = subprocess.run(cmd, capture_output=True,text=True)
    if sp.stderr :
        print("error cannot get active win!")
        print(sp.stderr)
        if not stillContine :
            exit(0) 
    else :
        return sp.stdout

def list_wm_ids(verbo=False):

    wmlist = []
    wmrun=bashrun(["wmctrl","-lx"])
    if wmrun is None :
        raise Exception("cannot fetch wmctrl list!")
    else :
        wmlist = wmrun.splitlines()

    if verbo : return wmlist
    decoder=lambda line : line.split(" ")[0]
    decodedlines=map(decoder,wmlist)
    return set(decodedlines)

#list_wm_ids()

def fetch_winId(xdotool_id) -> str:
    run = bashrun(["xwininfo","-id",xdotool_id])
    if run is None :
        raise Exception("Empty info!")
    else :
        lists=run.splitlines()

    # after this needle there an id!
    #0x01e00002
    idLength=10
    needle="Window id:" 

    nindex = lists[1].find(needle)
    nlen = needle.__len__()
    start = nindex+nlen
    res=lists[1][start:start+idLength]
    return res

def Retry(closure,retry_type=Exception,logger=None,sleep_time=0,limit=300):
    #intepret as infinity
    if limit == 0 :
        print("Warning! : infinite retries")
        limit=-1

    attempt=0
    
    if not callable(closure):
        print("argument need to be a function !")
        return

    def builtinLogger(info,err=False):
        print("builtinlog : {}\n".format(info)) 
        if err :
            traceback.format_exc()

    logger =  builtinLogger if logger is None or False and callable(logger) else logger
    Waitfor = lambda wait_time: time.sleep(wait_time) and logger("waiting...")
    noExcept = False
    while attempt < limit and not noExcept and limit != -1: 
        try :
            closure()
            noExcept = True
            break
        except Exception as ex:
            if not isinstance(ex,retry_type) :
                logger("Unexpected encounter from different exception",True)
                raise ex
            if attempt >= limit and limit > 0:
                logger("No more attempt left. Aborting",True)
                raise ex
        Waitfor(sleep_time)
        #print(attempt)
        attempt+=1

def get_wininfo(appname):
    if type(appname) != str :
        raise TypeError("bad typing accept only string!")

    raw_list=list_wm_ids(verbo=True)
    window_list={}

    for wm_inp in raw_list:

        applications = wm_inp.split()[2].lower()
        appwinid = wm_inp.split(None,1)[0].lower()
        workspace = wm_inp.split()[1]
        no_dot = applications.split(".",1)[0]
         
        window_list[no_dot] = {
                "workspace":workspace,
                "win_id":appwinid
        }

    return window_list[appname]["win_id"]



def getActivewin():
    winid = bashrun(["xdotool","getactivewindow"],stillContine=True)
    # for the handleEmpty to work
    if winid is None : return None
    xidhex = "{}".format(hex(int(winid)))

    head ,tail = xidhex.split("x")
    zeropadding = "00" if len(xidhex) + 2 == 10 else "0"

    return "{}x{}{}".format(head,zeropadding,tail).strip()

def getWorkspace(winTarget):
    # dump out all wmctrl -lx

    idlist = list_wm_ids(True)
    needle = winTarget
    print(idlist[0].split()[0],needle)
    finder = lambda wm_output : wm_output.split()[0] == needle

    res = list(filter(finder,idlist))
    print(res)
    workspace = res[0].split()[1]
    return workspace

#def fetchCurrentworkspace():
#    wmctrlList = []
#    try :
#        run = bashrun(["wmctrl","-d"])
#        if run is None :
#            exit(1)
#        wmctrlList = run.splitlines()
#
#        findasterix = lambda wm_inp: wm_inp.find(b"*") != -1
#        res = list(filter(findasterix,wmctrlList))[0]
#        # only get first ele
#        processWsNum = lambda res : res.decode().split()[0]
#        return processWsNum(res)
#    except :
#        raise Exception("Cannot fetch wmctrl -d")
   #print(wmctrlList.find(b'*'))

def fetchCurrentworkspace():
    try : 
        run = bashrun(["xdotool","get_desktop"])
        if run is None :
            exit(1)
        return run
    except Exception:
        traceback.print_exc()
        raise Exception("Cannot fetch get_desktop")


