# start paramatize
#import daemon
from wmctrl_lib import *
import subprocess
import traceback
import abc
import os.path
import time

from multiprocessing import Pool
import threading

#Retry("hahahah")
# attempting to rewrite spotify scripts
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
        if path is None:
            path = "/tmp/toggle_spot.txt"

        if not os.path.isfile(path) and not os.path.exists(path):
            with open(path,"w") as f:
                #f.write("{}:false".format(self._prefix))
                print("Creating file!")
    
        self.fstate = open(path, "r")
        self.state = ""
        self.path = path

        self.window_id = ""
        self.last_window = ""
        self.cache_window = ""

    def pinState(self,pstr):
        spt = pstr.split(":")
        res = {
            "isState" : False,
            "value" : ""
        }
        if len(spt) > 2:
            print("Wrong semantic")
            return res
        else:
            res["isState"] =spt[0] == self._prefix
            res["value"] = spt[1].strip()

        return res
    

    #Preimplemented Method
    #toggle status is set into

    def persistanceToggle(self):

        if self.state == "false":
            self.state = "true"
        else:
            self.state = "false"
        print("bruh",self.state)


    @staticmethod        
    def run(appname):
        proc_name = appname
        if "-" in appname:
            print("Get first in split")
            proc_name = appname.split("-")[0]
            print(proc_name)

        return len(bashrun(["pgrep",proc_name])) > 0
    

    @staticmethod
    def spawnApp(appname,exec_bash):
        if not WindowPinner.run(appname):
            print("no app is running, launching")
            if appname == "spotify":
                exec_bash=["/mnt/coding/system-testing/spt-musc"]
            openning = lambda : subprocess.Popen(exec_bash,shell=False)
            subprocess.call(exec_bash)
            return
    
    # trranslate state in file to boolean
    def translateToBool(self):
        print("translate to bool")
        primaryState = "true"
        self.state = self.state == primaryState

    @staticmethod
    def buildGoto(appid):
        goto = lambda : bashrun(["wmctrl","-ia","{}".format(appid.strip()).strip()])
        return goto

    # use to build addtional /different mode of toggle
    def appToggleCore(self,appid,exec_bash):

        self.pinToggle()
        self.translateToBool()
        #self.persistanceToggle()
        if not isinstance(exec_bash,list):
            print("not a list!")
            return
         

        gotoApp = self.buildGoto(appid)
        awin = getActivewin()

        if self.last_window is None:
            if self.handleEmptywin(gotoApp):
                return

        gotoPrev = self.buildGoto(self.last_window)
    
        #self.translateToBool() 
        #print("from app toggle core",self.state)
        #print("awin",awin,appid,self.isLastwin())
        #print("lastwindow",self.last_window)
        print("This is last window =>>>>>>>>>>>",self.last_window)
        
        if self.last_window == appid :
            print("function break down!")
            exit(1)
        
        if awin == appid:
            gotoPrev()
            #Retry(gotoPrev,sleep_time=0.05)
            print("Current window is app")
            return 

        if self.isLastwin() and self.last_window != appid:
            gotoApp()
            return
        
        elif awin != appid : 
            gotoApp()
            return

        returnToPrev = lambda : self.state  or awin == appid 
        #and awin != self.last_window
        print("return?",returnToPrev())
        if returnToPrev():
            gotoPrev()
        else:
            Retry(gotoApp)
    
    def handleEmptywin(self,gotoApp):
        print("Empty window id")
        print(self.last_window)
        if self.last_window is None and self.state == False:
            ws=fetchCurrentworkspace()
            if self.cache_window is None :
                print("setting cache")
                self.cache_window = ws
                gotoApp()
            else:
                print("going back")
                bashrun(["wmctrl","-s {}".format(self.cache_window).strip()])
            print("cache window",self.cache_window)
            return True

    def appToggle(self,appname,exec_bash):
        WindowPinner.spawnApp(appname,exec_bash)
        print("wininfo",get_wininfo(appname))
        appid = get_wininfo(appname)
        #self.pinToggle()
        self.appToggleCore(appid,exec_bash=exec_bash)

    def isLastwin(self):
        ati = getActivewin()
        return ati == self.last_window


#print("current window",getActivewin())

#spt.spotify_open()

#get_wininfo("brave-browser")

def build_get_wininfo(keytype,wininput):
    #wmlist=bashrun(["wmctrl","-lx"]).splitlines()

    raw_list=list_wm_ids(verbo=True)
    window_list={}
    for wm_inp in raw_list:

        applications = wm_inp.decode().split()[2].lower()
        appwinid = wm_inp.decode().split(None,1)[0].lower()
        workspace = wm_inp.decode().split()[1]
        name = applications.split(".",1)[0]

        key = appwinid if keytype == "id" else name
        window_list[key] = {
                "workspace":workspace,
                "win_id":appwinid,
                "appname":name
        }
        #set([[wm_inp,]])
        #print(wm_inp)
    
    if wininput in window_list: 
        print(window_list[wininput]["appname"])

    return window_list[wininput]["win_id"]
    #print(args.__dict__[i])
#print(args.__dict__["toggle"])

class WindowPinner(WindowPinnerCore):
    def __init__(self,path):
        super().__init__(path)

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

            On=self.pinState(lines[0].strip())
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

    def lockMechanism(self):
        print("not implemented!")


#pin_test = WindowPinner("/tmp/toggle_spot.txt")
#pin_test.appToggle("brave-browser",["brave"])
