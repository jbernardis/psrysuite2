import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
    sys.path.insert(0, cmdFolder)
 

from subprocess import Popen, STARTUPINFO, STARTF_USESHOWWINDOW, DEVNULL
   
from dispatcher.settings import Settings

SW_MINIMIZE = 6
infoMinimize = STARTUPINFO()
infoMinimize.dwFlags = STARTF_USESHOWWINDOW
infoMinimize.wShowWindow = SW_MINIMIZE

np = len(sys.argv)

if np < 2:
    mode = "dispatcher"

else:
    mode = sys.argv[1]
        
ofp = open(os.path.join(os.getcwd(), "output", ("launch%s.out" % mode)), "w")
efp = open(os.path.join(os.getcwd(), "output", ("launch%s.err" % mode)), "w")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()

interpreter = sys.executable.replace("python.exe", "pythonw.exe")
interpfg    = sys.executable.replace("pythonw.exe", "python.exe")
 
for i in range(len(sys.argv)):
    print("%d: %s" % (i, sys.argv[i]))

if mode == "remotedispatcher":
    print("Launch mode: remote dispatcher")
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--dispatch"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
 
elif mode == "dispatcher":
    print("Launch mode: dispatcher suite")
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec, "--nosim"], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--dispatch"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)

elif mode == "satellite":
    print("launch mode: satellite")

    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--satellite"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("satellite dispatcher started as PID %d" % dispProc.pid)

elif mode == "simulation":
    print("launch mode: simulation")
    
    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    print("server exec = (%s)" % svrExec)
    print("Interpreter = (%s)" % interpfg)
    svrProc = Popen([interpfg, svrExec, "--sim"], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)
    
    simExec = os.path.join(os.getcwd(), "trafficgen", "main.py")
    simProc = Popen([interpreter, simExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("trafficgen started as PID %d" % simProc.pid)
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--dispatch"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)
    
    monExec = os.path.join(os.getcwd(), "monitor", "main.py")
    monProc = Popen([interpreter, monExec, "--sim"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("monitor started as PID %d" % monProc.pid)

elif mode == "display":
    print("launch mode: display")

    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--display"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)

elif mode == "cliffdisplay":
    print("launch mode: cliff display")

    dispExec = os.path.join(os.getcwd(), "cliffdisplay", "main.py")
    dispProc = Popen([interpreter, dispExec, "--display"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)

elif mode == "dispatcheronly":
    print("launch mode: dispatcher only")
    
    dispExec = os.path.join(os.getcwd(), "dispatcher", "main.py")
    dispProc = Popen([interpreter, dispExec, "--dispatch"], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
    print("dispatcher started as PID %d" % dispProc.pid)

elif mode == "serveronly":
    print("launch mode: server only")

    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec, "--nosim"], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)

elif mode == "serveronlysim":
    print("launch mode: server only - simulation mode")

    svrExec = os.path.join(os.getcwd(), "rrserver", "main.py")
    svrProc = Popen([interpfg, svrExec, "--sim"], startupinfo=infoMinimize)
    print("server started as PID %d" % svrProc.pid)

else:
    print("Unknown mode.  Must specify either 'dispatcher', 'remote dispatch', 'simulation', 'display', 'dispatcheronly', 'serveronly', or 'serveronlysim'")
    
print("launcher exiting")  

 

