import time
import timeit
import subprocess
from wmctrl_lib import *
#import numpy

prev = 0 
cur = 0

def pingXdotool(pollrate,limit=None):

    if limit is None :
        limit = float('inf')

    getws = lambda : subprocess.run(["xdotool","get_desktop"],capture_output=True).stdout.decode()
    cur = getws()
    count = 0

    while count < limit:
        time.sleep(pollrate)
        ws = getws()

        prev = cur 
        cur = ws

        if prev != cur :
            print(getActivewin())
            print("workspace has change!")
            #exit(1)

        count += 1

goto = lambda ws:subprocess.run(["wmctrl","-s {}".format(ws)],capture_output=True).stdout.decode()

def get_wininfo2(appname):
    #wmlist=bashrun(["wmctrl","-lx"]).splitlines()
    if type(appname) != str :
        raise TypeError("bad typing accept only string!")

    raw_list=list_wm_ids(verbo=True)
    window_list={}
    for wm_inp in raw_list:
        splt = wm_inp.split()
        applications = splt[2].lower()
        appwinid = splt[0].lower()

        #workspace = splt[1]
        no_dot = applications.split(".",1)[0]
        if appname == no_dot :
            return appwinid
        #window_list[no_dot] = {
        #        "workspace":workspace,
        #        "win_id":appwinid
        #}

    return window_list[appname]["win_id"]

def get_wininfo3(appname=""):
    if type(appname) != str :
        raise TypeError("bad typing accept only string!")
    winid = bashrun(["xdotool","getactivewindow"]).strip()
    h = "{}".format(hex(int(winid)))
    print(h)
    head ,tail = h.split("x")
    return "{}x00{}".format(head,tail)

def gotoHook(ws):
    print(getActivewin())
    goto(ws)


def traverseNp(arr):
    for i in arr:
        if i is None or i == 0:
            b = 0

#import numpy
from winpin_daemon import cacheCleaner

if __name__ == "__main__":

    nor = [0 for i in range(10)]
    #import timeit
    #print(timeit.timeit(lambda:getActivewin(), setup="from __main__ import gotoHook"))
    #print(timeit.timeit(lambda:print(getWorkspace(getActivewin())),number=1))
    
    cleancache = cacheCleaner.buildresetArray(nor)
    print(timeit.timeit(lambda:cleancache(keepElement=2)))
    print("compare ac",getActivewin() == get_wininfo3())
    import os 

    print(os.forkpty())



