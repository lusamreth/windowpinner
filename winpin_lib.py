# start paramatize
#import daemon

from wmctrl_lib import *
import subprocess
import traceback
import abc
import os.path
import time

import os
from multiprocessing import Pool
import threading

def spawnApp(appname,exec_bash):
    print("calling spawnApp ==== ")
    print(isRunning(appname))
    if not isRunning(appname):
        print("no app is running, launching")
        if appname == "spotify":
            exec_bash=["/mnt/coding/system-testing/spt-musc"]

        subprocess.Popen(exec_bash, close_fds=True)
        return

def isRunning(appname):
    print("callingis running",appname)
    proc_name = appname
    if "-" in appname:
        print("Get first in split")
        proc_name = appname.split("-")[0]
        print(proc_name)
    r = bashrun(["pgrep",proc_name])

    if r is not None :
        return len(r) > 0

    return False

#Retry("hahahah")
# attempting to rewrite spotify scripts
def initFstate(path):
    if path is None:
        path = "/tmp/toggle_spot.txt"

    if not os.path.isfile(path) and not os.path.exists(path):
        with open(path,"w"):
            #f.write("{}:false".format(self._prefix))
            print("Creating file!")
    return open(path, "r")

def buildGoto(appid):
    goto = lambda : bashrun(["wmctrl","-ia","{}".format(appid.strip()).strip()])
    return goto

def readState(_prefix,pstr):
    spt = pstr.split(":")
    res = {
        "isState" : False,
        "value" : ""
    }
    if len(spt) > 2:
        print("Wrong semantic")
        return res
    else:
        res["isState"] =spt[0] == _prefix
        res["value"] = spt[1].strip()

    return res

class WindowPinnerCore(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def lockMechanism(self):
        raise NotImplementedError
   
    @abc.abstractmethod
    def pinToggle(self):
        """Load in the data set"""
        raise NotImplementedError

    def __init__(self,path):

        self._prefix = "toggle_state"
        # fstate is called the filestate !
        self.state = ""
        self.path = path

        self.window_id = ""
        self.last_window = ""
        self.cache_window = ""
    
    
    #Preimplemented Method
    #toggle status is set into

    

    
    # translate state in file to boolean
    def translateToBool(self):
        primaryState = "true"
        self.state = self.state == primaryState

    def handleEmptywin(self,gotoApp):
        ws=fetchCurrentworkspace()
        if self.state == False:
            self.cache_window = ws
            gotoApp()
        else :
            bashrun(["wmctrl","-s {}".format(self.cache_window).strip()])

        return 


    def isLastwin(self):
        ati = getActivewin()
        return ati == self.last_window


    # use to build addtional /different mode of toggle
    def appToggleCore(self,appid):

        self.pinToggle()
        awin = getActivewin()
        #self.translateToBool()

        gotoApp = buildGoto(appid)

        if self.last_window is None:
            self.handleEmptywin(gotoApp)
            return

        gotoPrev = buildGoto(self.last_window)

        if awin == appid:
            gotoPrev()
            return 
    
        if self.isLastwin() and self.last_window != appid:
            gotoApp()
            return
        
        if awin != appid : 
            gotoApp()
            return

        returnToPrev = lambda : self.state  or awin == appid 
        if returnToPrev():
            gotoPrev()
        else:
            Retry(gotoApp)
    


#print("current window",getActivewin())

#spt.spotify_open()

#get_wininfo("brave-browser")

def build_get_wininfo(keytype,wininput):
    #wmlist=bashrun(["wmctrl","-lx"]).splitlines()

    raw_list=list_wm_ids(verbo=True)
    window_list={}
    for wm_inp_raw in raw_list:
        wm_inp = wm_inp_raw.decode()

        applications = wm_inp.split()[2].lower()
        appwinid = wm_inp.split(None,1)[0].lower()
        workspace = wm_inp.split()[1]
        name = applications.split(".",1)[0]

        key = appwinid if keytype == "id" else name
        window_list[key] = {
                "workspace":workspace,
                "win_id":appwinid,
                "appname":name
        }
        #set([[wm_inp,]])
        #print(wm_inp)

    return window_list[wininput]["win_id"]
    #print(args.__dict__[i])
#print(args.__dict__["toggle"])

class WindowPinner(WindowPinnerCore):

    def __init__(self,path):
        super().__init__(path)
        self.fstate = initFstate(path)

    def pinToggle(self):
        print("bruhtoggle from normal file")
        # cache in line 2
        lines = self.fstate.readlines()
        retrieved_state = "false"

        awin = getActivewin()
        wid="last_window_id:{}".format(awin)
        writemodefile=open(self.path,"w")
        #print("is last window",self.isLastwin())
        if len(lines) > 0 :

            last_win = lines[1].split(":")
            print("lastwind",last_win[1])
            self.last_window = last_win[1].strip()

            On=readState(self._prefix,lines[0].strip())
            onVal=On["value"]
            if On["isState"] == True:
                fstate=onVal
                # if state is empty it mean early access!
                # initial value is always True
                if fstate == "true" or self.isLastwin():
                    retrieved_state = "false" 
                else :
                    retrieved_state = "true" 
                
                self.state = fstate 
                tar="{0}:{1}".format(self._prefix,retrieved_state)
                # only stores last window id 
                content="{}\n{}".format(tar,wid)
                Retry(lambda : writemodefile.write(content),limit=100)
                #writemodefile.write(content)
        else :
            self.state = retrieved_state
            print(awin)
            self.last_window = awin
            Retry(writemodefile.write("{}:{}\n{}".format(self._prefix,retrieved_state,wid)),limit=30)
            print("default is false!")

        writemodefile.close() 


    def appToggle(self,appname,exec_bash):
        spawnApp(appname,exec_bash)
        appid = get_wininfo(appname)
        self.appToggleCore(appid)

    def lockMechanism(self):
        print("no")
#pin_test = WindowPinner("/tmp/toggle_spot.txt")
#pin_test.appToggle("brave-browser",["brave"])
