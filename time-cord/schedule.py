# schedule using launchd for mac os x NOT CRONTAB
import platform, os, sys, pwd

if platform.system() == "Darwin":
    pypaths = sys.path # get python path environment
    finals = []
    for p in pypaths:
        finals.append(p.split("/")[-1])
    ind = -1
    for f in range(len(finals)):
        if finals[f][0:6] != "python":
            continue
        if not finals[f][6:].replace('.','',1).isdigit():
            continue
        if ind != -1:
            raise Exception("Python path parsing failed: too many choices")
        ind = f
    if ind == -1:
        raise Exception("Python path parsing failed: no valid python path")
    pypath = sys.path[ind]
    pypath_split = pypath.split("/")
    pypath_split[-2] = "bin"
    pypath = "/".join(pypath_split)
    print(pypath)

    path = os.path.realpath(__file__)
    path_split = path.split("/")
    path_split[-1] = ""
    path = "/".join(path_split)
    print(path)
    
    str = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>timecord.app</string>
		<key>ProgramArguments</key>
        <array>
            <string>""" + pypath + """</string>
            <string>""" + path + """run.py</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
	    <key>StandardOutPath</key>
	    <string>""" + path + """out.log</string>
	    <key>StandardErrorPath</key>
	    <string>""" + path + """out.log</string>
	</dict>
</plist>"""
    in_path = "/Users/" + pwd.getpwuid(os.getuid()).pw_name + "/Library/LaunchAgents/timecord.app.plist"
    print(in_path)
    command = "launchctl unload " + in_path
    os.system(command)
    with open(in_path, "w") as file:
        file.write(str)
    command = "launchctl load " + in_path
    os.system(command)
elif platform.system() == "Windows":
    raise Exception(platform.system() + " is not supported by this version of time-cord.")
else:
    raise Exception(platform.system() + " is not supported by this version of time-cord.")
