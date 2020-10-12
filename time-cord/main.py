from subprocess import Popen, PIPE
import time, platform

if platform.system() == "Windows"
    """
    Windows-only imports; these will fail on MacOS
    """
    import win32process
    import wmi
    import win32gui

time.sleep(3)

class UnsupportedOSError(Exception):
    """
    Handles the case of users running on Windows/Linux.
    """

def return_top():
    """
    Return name and title of the focused window in string format in supported OSes. 
    
    Code adapted from: Albert's answer (https://stackoverflow.com/questions/5292204/macosx-get-foremost-window-title)
        and RobC's answer (https://stackoverflow.com/questions/51775132/how-to-get-return-value-from-applescript-in-python)
    
    Returns:
      str: "name, title"
    """

    if platform.system() == "Darwin":
        frontapp = '''
            global frontApp, frontAppName, windowTitle
            set windowTitle to ""
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
                tell process frontAppName
                    tell (1st window whose value of attribute "AXMain" is true)
                        set windowTitle to value of attribute "AXTitle"
                    end tell
                end tell
            end tell
            return {frontAppName, windowTitle}
          '''

        proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        front, error = proc.communicate(frontapp)
        return front

    elif platform.system() == "Windows":
        front = psutil.Process(win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[-1]).name()

    else:
        raise UnsupportedOSError(platform.system() + " is not supported by this version of time-cord.")

def is_open():
    """
    Determine if Discord is open in the top window, and return current channel name if so.
    
    Returns:
      boolean: Whether Discord is open
      str: channel_name if Discord is open, else None
    """
    top = return_top()
    if top[0:8] == "Discord,":
        hash = top.index("#")
        top = top[hash + 1:]
        space = top.index(" ")
        top = top[:space]
        return True, top
    else:
        return False, None

# TODO: a function which can find the server name in Discord (return_top has the ability to find the channel name.)

print(return_top())
print(is_open())