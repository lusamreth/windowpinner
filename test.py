import subprocess 


p = subprocess.Popen("/bedrock/cross/bin/brave",close_fds=True)
p.wait()
subprocess.Popen("/mnt/coding/system-testing/spt-musc",close_fds=True)
