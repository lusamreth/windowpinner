from wmctrl_lib import bashrun
def notify(msg):
    bashrun(["notify-send",msg])

notify("bruh")

