# finish this please
# ALmost There!
from wmctrl_lib import getActivewin,get_wininfo
from dasbus.server.interface import dbus_interface
from dasbus.connection import SessionMessageBus
from dasbus.typing import Str,Bool,Int32

from winpin_lib import WindowPinnerCore,spawnApp
from dasbus.loop import EventLoop

import os
import time
import subprocess

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
AppIdCache = dict()

@dbus_interface("org.example.WindowPinnerD")
class WindowPinnerDInterface(InterfaceTemplate):

    def AppToggle(self,appname:Str,startapp:Str):
        # require state to have app id 
        print("running appnak",appname,startapp)
        if AppIdCache.__len__() == 0 or not appname in AppIdCache:
            spawnApp(appname,startapp)
            AppIdCache[appname] = get_wininfo(appname)
        
        appid = AppIdCache[appname]
            
        print("{}:{}".format(appname,appid))
        GlobalState.appid = appid

        # call app toggle
        self.implementation.appToggleCore(appid)
        # app toggle then call togglePin which implemented togglePinCore
        
    def Pid(self) -> Int32:
        return self.implementation.pid()

    def PingD(self) -> Str:
        return self.implementation.ping()
    
    def Lock(self):
        print("locking")
        #pingXdotool(0.0005)
        print("after lock")
        self.implementation.lockMechanism()
    
#asyncio.new_event_loop()

State = True
WinIdCache = []

class cacheCleaner:
    @staticmethod
    def buildresetArray(arr):
        return lambda keepElement:resetArrayFactory(arr,traverseLength=keepElement)

def grabEndFactory(cacheArray,tempArr):
    cacheLen = len(cacheArray) - 1
    ar = tempArr

    # prevent reversed array
    def traverseBackCache(traverseLength):
        tmp = []
        [tmp.append(cacheArray[cacheLen - i]) for i in range(traverseLength)]
        assert len(tmp) > 0
        tmp.reverse()
        tempArr = ar
        
        [tempArr.append(i) for i in tmp]

    #traverseBackCache = lambda traverseLength : [tempArr.append(cacheArray[cacheLen -
    #    i]) for i in range(traverseLength)]
    return traverseBackCache

def resetArrayFactory(cacheArray,traverseLength):
    assert len(cacheArray) > traverseLength

    tempArr = []
    copyTmpToCache = lambda tempArr : [cacheArray.append(tempArr[i]) for i in range(traverseLength)]

    grabEnd = grabEndFactory(cacheArray,tempArr)
    grabEnd(traverseLength)

    cacheArray.clear()
    copyTmpToCache(tempArr)

Locker = dict()
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
    
    @staticmethod
    def checkInCache(last_window):
        print("cache ===> ",AppIdCache)
        for key in AppIdCache:
            #print("ccc",last_window,AppIdCache[key].strip())
            if last_window == AppIdCache[key].strip():
                print("bruh true")
                return True

    
    def pinToggle(self):

        GlobalState.reverse()

        struct = StateData.to_structure(GlobalState)
        self.state = not struct["state"]
        awin = getActivewin()

        WinIdCache.append(awin)
        appid = "{}".format(struct["appid"]).strip().replace("'","")
        isApp = WindowPinnerD.checkInCache(awin)

        l = len(WinIdCache)
        last2ndItem = WinIdCache[l - 2]
        last1stItem = WinIdCache[l - 1]

        resetter = cacheCleaner().buildresetArray(WinIdCache)
        if len(WinIdCache) > 10:
            resetter(keepElement=4)
        

        if isApp or WindowPinnerD.checkInCache(last1stItem):
            self.last_window = last2ndItem
            return

        if awin == appid :
            print("Dont set last window ===>?",appid)
            return
        
        
        if not self.state or awin != appid:
            self.cache_window = None
            self.last_window = awin
    

    def autoadjustLastWin(self,pollrate,limit=None):
        if limit is None :
            limit = int('inf')

        getws = lambda : subprocess.run(["xdotool","get_desktop"],capture_output=True).stdout.decode()
        cur = getws()
        count = 0

        while count < limit:
            time.sleep(1/pollrate)
            ws = getws()

            prev = cur 
            cur = ws

            if prev != cur :
                print("workspace has change!")
                self.isChanged = True
                self.last_window = getActivewin()
                #exit(1)
            count += 1

    def lockMechanism(self):
        awin = getActivewin()
        GlobalState.appid = awin 
        print("locking")
        self.appToggleCore(awin)


from dasbus.server.container import DBusContainer

AppPath = "/tmp/winpinner"
pidfilepath = os.path.join(AppPath, "windowpinDaemon.pid")

#def stampPid():
#
#    if not os.path.exists(AppPath):
#        os.mkdir(AppPath)
#    elif not os.path.isfile(pidfilepath):
#        with open(pidfilepath,"x") as F:
#            print(os.getpid())
#            F.write("{}".format(os.getpid()))
#    else:
#        with open(pidfilepath,"w") as F:
#            print(os.getpid())
#            F.write("{}".format(os.getpid()))
#        print("pre-start hook is setup! Proceeding...")

import atexit

from time import sleep
from daemonize import Daemonize

pid = "/tmp/test.pid"


def preDestroyHook():
    with open(pidfilepath,"w") as F:
        print(os.getpid())
        print("pre destroy hook!")
        F.write("")


def spinUpDaemon():
    print("stamp")
    #stampPid()

    container = DBusContainer(
        namespace=("org", "winpinner", "WindowPinnerD"),
        message_bus=SessionMessageBus()
    )


    container.to_object_path(WindowPinnerD())
    print("Starting winpinner daemon!")

    bus.register_service("org.example.WindowPinnerD")
    #atexit.register(preDestroyHook)
    loop.run()


if __name__ == "__main__":
    spinUpDaemon()

import unittest

def mockResetter(rangeNum,keepElement):
    arr = []
    [arr.append(x) for x in range(rangeNum)]
    cleaner = cacheCleaner().buildresetArray(arr)
    cleaner(keepElement)
    return arr

def mockGrab(rangeNum,grablastElementRange):
    temp = []
    cacheExample = []

    [cacheExample.append(x) for x in range(rangeNum)]

    grabE = grabEndFactory(cacheExample,temp)
    grabE(grablastElementRange)
    return temp

class testTraverser(unittest.TestCase):

    def testGrepEle(self):
        temp = mockGrab(rangeNum=10,grablastElementRange=2)    
        last2items = [8,9]

        #assert temp == last2items
        self.assertTrue(temp == last2items)

    def testResetter(self):
        cacheExample = mockResetter(10,2)
        
        expectRes = [8,9]
        self.assertTrue(expectRes == cacheExample)

    def testIfReversed(self):
        NotExpect = [9,8]
        self.assertFalse(NotExpect == mockResetter(10,2))
        
    def testIfGrabReversed(self):
        NotExpect = [9,8]
        temp = mockGrab(rangeNum=10,grablastElementRange=2)    
        self.assertFalse(NotExpect == temp)




