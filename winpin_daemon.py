# finish this please
from wmctrl_lib import getActivewin,get_wininfo

from dasbus.server.interface import dbus_interface
from dasbus.connection import SessionMessageBus
from dasbus.typing import Str,Bool,Int32

from winpin_lib import WindowPinnerCore
from dasbus.loop import EventLoop

from daemonize import Daemonize
import os
loop = EventLoop()

bus = SessionMessageBus()
state=True


from dasbus.server.template import InterfaceTemplate
from dasbus.server.publishable import Publishable
from dasbus.structure import DBusData

class StateData(DBusData):
    def __init__(self):
        self._state = False
        self._app_id = ""

    @property
    def state(self) -> Bool:
        return self._state

    @state.setter
    def state(self,state) :
        self._state = state

    @property
    def appid(self) -> Str:
        return self._appid

    @appid.setter
    def appid(self,inputid) :
        self._appid = inputid

    def reverse(self):
        self._state = not self._state

GlobalState = StateData()
Cache = dict()
@dbus_interface("org.example.WindowPinnerD")
class WindowPinnerDInterface(InterfaceTemplate):

    def AppToggle(self,appname:Str,startapp:Str):
        # require state to have app id 
        print(appname,startapp)
        self.implementation.spawnApp(appname,startapp)
        if Cache.__len__() == 0 or not appname in Cache:
            Cache[appname] = get_wininfo(appname)

        appid = Cache[appname]
        print("{}:{}".format(appname,appid))
        GlobalState.appid = appid

        # call app toggle
        self.implementation.appToggleCore(appid,[startapp])
        # app toggle then call togglePin which implemented togglePinCore
        
    def Pid(self) -> Int32:
        return self.implementation.pid()

    def PingD(self) -> Str:
        return self.implementation.ping()

    def Lock(self):
        print("lockhin")
        self.implementation.lockMechanism()
    

State = True
class WindowPinnerD(Publishable,WindowPinnerCore):

    def __init__(self):
        self.lastwinid = ""
        self.lock_id = ""

    def ping(self):
        return "pong"

    def pid(self):
        return os.pid()

    def for_publication(self):
        return WindowPinnerDInterface(self)
    
    def pinToggle(self):

        GlobalState.reverse()

        struct = StateData.to_structure(GlobalState)
        self.state = not struct["state"]
        #self.appid = struct["appid"]
        #try :
        #    awin = getActivewin()
        #except Exception:
        #    print("cannot get window")
        #    return
        awin = getActivewin()


        appid = "{}".format(struct["appid"]).strip().replace("'","")
        #print("This is active window =>>>>>>>>>>>",awin,self.state)
        if awin == appid:
            print("Dont set last window ===>?",appid)
            return
        
        if not self.state or awin != appid:
            self.cache_window = None
            self.last_window = awin
    
    def lockMechanism(self):
        # put the name inside the cache 
        # just like the app name
        print("hello")


from dasbus.server.container import DBusContainer

AppPath = "/tmp/winpinner"
pidfilepath = os.path.join(AppPath, "windowpinDaemon.pid")

def stampPid():

    if not os.path.exists(AppPath):
        os.mkdir(AppPath)
    elif not os.path.isfile(pidfilepath):
        with open(pidfilepath,"x") as F:
            print(os.getpid())
            F.write("{}".format(os.getpid()))
    else:
        with open(pidfilepath,"w") as F:
            print(os.getpid())
            F.write("{}".format(os.getpid()))
        print("pre-start hook is setup! Proceeding...")

import atexit

from time import sleep
from daemonize import Daemonize

pid = "/tmp/test.pid"


def preDestroyHook():
    with open(pidfilepath,"w") as F:
        print(os.getpid())
        print("pre destroy hook!")
        F.write("")

def testDaemon():
    import logging
    import sys

    child_logger = logging.getLogger("tba")
    child_logger.setLevel(logging.DEBUG)
    child_logger.addHandler(logging.FileHandler("/tmp/test.txt"))
    #streamhdr = logging.StreamHandler(sys.stdout)
    while True:
        sleep(2)
        child_logger.debug("bruh stop it mtf")


def spinUpDaemon():
    print("stamp")
    stampPid()

    container = DBusContainer(
        namespace=("org", "winpinner", "WindowPinnerD"),
        message_bus=SessionMessageBus()
    )


    container.to_object_path(WindowPinnerD())
    print("Starting winpinner daemon!")

    bus.register_service("org.example.WindowPinnerD")
    atexit.register(preDestroyHook)
    loop.run()

if __name__ == "__main__":

    #daemon.start()
    spinUpDaemon()