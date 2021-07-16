#!/bin/python3

import argparse
from winpin_lib import WindowPinner ,Retry
from dasbus.connection import  SessionMessageBus
from winpin_daemon import spinUpDaemon

parser = argparse.ArgumentParser(
    description='This program prints a color HEX value'
)

Pinner = WindowPinner("/tmp/toggle_spot.txt")

parser.add_argument('-l', '--lock', metavar='lock', required=False,
        help='command to lock window')
parser.add_argument('-t', '--toggle', metavar='toggle', required=False,
        help='command to toggle window')
parser.add_argument('-s', '--spawn', metavar='spawn', required=False,
        help='command to run app use with toggle!')
parser.add_argument('-d','--daemon',action="store_true",required=False,
        help='Spawn Daemon Bro!')
    
bus = SessionMessageBus()
winpinProxy = bus.get_proxy(
    "org.example.WindowPinnerD",
    "/org/winpinner/WindowPinnerD/1"
)

args = parser.parse_args()

def checkIfDaemonRuning(dbuspid):

    pidFilePath = "/tmp/winpinner/windowpinDaemon.pid"
    isRunning = False
    
    with open(pidFilePath,"w") as pidFile:
        pid = pidFile.read()
        print("Daemon running on pid: {}".format(pid))
        if dbuspid != pid:
           pidFile.write(dbuspid) 

        isRunning = pidFile.read() is not None 

    return isRunning

    
def prompting(message,closure):
    
    if not callable(closure):
        print("cannot call this function",closure.__name__)
        return

    ans = input("{} [y/n]".format(message)).lower()

    if ans == "y" or ans == "yes" :
        closure()
    elif ans == "n" or ans == "no":
        exit(1)
    else :
        print("please enter yes or no!")

import subprocess

def activate_toggle(args):

    #r.run()

    run = None
    #prompt = lambda : prompting("Do you want to restart daemon?",lambda:subprocess.Popen(["./winpinCli.py","-d"]))
    prompt = lambda : prompting("Do you want to restart daemon?",spinUpDaemon)


    def commDaemon():
        Ping = None
        try :
            Ping = winpinProxy.PingD()
        except Exception:
            print("cannot ping dbus")
            prompt()

        #assert(Ping is not None)
        return Ping

    if args.daemon : 
        if not args.spawn :
            print("require spawn argument!")
            exit(1)
        run = commDaemon()

    if run == "pong" and args.daemon:
        winpinProxy.Pid
        try:
            winpinProxy.AppToggle(args.toggle,args.spawn)
        except Exception as Error:

            print("Cannot Toggle application!")
            print("Please restart your daemon")

            raise Error
    else :    
        Pinner.appToggle(args.toggle,[args.spawn])



for arg in args.__dict__:
    arg_input=args.__dict__[arg]
    if arg_input is not None:
        if arg == "toggle":
            print("activating toggle!")
            activate_toggle(args)
        elif arg == "lock":
            print("locking")



#ignore the error! it actually callable
#bruh = winpinProxy.PinToggle()
#proxy.appToggleMethod("brave-browser","brave")
