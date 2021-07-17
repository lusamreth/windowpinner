
import subprocess
import traceback
import os.path
import time

# execute command
def bashrun(cmd,stillContine=False):
    sp = subprocess.run(cmd, capture_output=True)

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
    decoder=lambda line : line.decode().split(" ")[0]
    decodedlines=map(decoder,wmlist)
    return set(decodedlines)

list_wm_ids()

def fetch_winId(xdotool_id):
    run = bashrun(["xwininfo","-id",xdotool_id])
    if run is None :
        raise Exception("Empty info!")
    else :
        lists=run.splitlines()

    # after this needle there an id!
    #0x01e00002
    idLength=10
    needle=b"Window id:" 

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
    #wmlist=bashrun(["wmctrl","-lx"]).splitlines()
    if type(appname) != str :
        raise TypeError("bad typing accept only string!")

    raw_list=list_wm_ids(verbo=True)
    window_list={}
    for wm_inp in raw_list:

        applications = wm_inp.decode().split()[2].lower()
        appwinid = wm_inp.decode().split(None,1)[0].lower()
        workspace = wm_inp.decode().split()[1]
        no_dot = applications.split(".",1)[0]
    
        window_list[no_dot] = {
                "workspace":workspace,
                "win_id":appwinid
        }
        #set([[wm_inp,]])
        #print(wm_inp)

    return window_list[appname]["win_id"]


def getActivewin():
    xid = bashrun(["xdotool", "getactivewindow"],stillContine=True)
    if xid is None:
        print("Empty window id!")
    else:
        wid = fetch_winId(xid.strip().decode()).strip().decode()
        l = len(wid)

        def getI(eid):
            lhs = eid.strip()[3:len(eid)]
            rhs = wid[2:l]
            # sometimes rhs(id from xdotool is shorter than wmctl_id)
            if len(rhs) < len (lhs):
                rhs="0{0}".format(rhs)

            assert(len(lhs) == len(rhs))
            return lhs == rhs
        Winid = filter(lambda eid: getI(eid),list_wm_ids())
        return list(Winid)[0]

def getWorkspace(winTarget):
    # dump out all wmctrl -lx

    idlist = list_wm_ids(True)
    needle = winTarget.encode()

    finder = lambda wm_output : wm_output.split()[0] == needle

    res = list(filter(finder,idlist))
    workspace = res[0].split()[1].decode()
    return workspace

def fetchCurrentworkspace():
    wmctrlList = []
    try :
        run = bashrun(["wmctrl","-d"])
        if run is None :
            exit(1)
        wmctrlList = run.splitlines()

        findasterix = lambda wm_inp: wm_inp.find(b"*") != -1
        res = list(filter(findasterix,wmctrlList))[0]
        # only get first ele
        processWsNum = lambda res : res.decode().split()[0]
        return processWsNum(res)
    except :
        raise Exception("Cannot fetch wmctrl -d")
   #print(wmctrlList.find(b'*'))

