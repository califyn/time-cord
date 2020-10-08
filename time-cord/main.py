from subprocess import Popen, PIPE
import time

time.sleep(3)

def get_top_window():
    """Return name and title of the focused window in MacOSX. 
    
    Code adapted from: Albert's answer (https://stackoverflow.com/questions/5292204/macosx-get-foremost-window-title) and RobC's answer (https://stackoverflow.com/questions/51775132/how-to-get-return-value-from-applescript-in-python)
    
    Returns:
    str: "name, title"
    """
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

def is_open():
    """Determine if Discord is open in the top window

    Returns:
    boolean: Whether Discord is open
    str: channel_name if Discord is open, else None
    """
    top = get_top_window()
    if top[0:8] == "Discord,":
        hash = top.index("#")
        top = top[hash + 1:]
        space = top.index(" ")
        top = top[:space]
        return True, top
    else:
        return False, None

# TODO: a function which can find the server name in Discord (get_top_window has the ability to find the channel name.)

print(get_top_window())
print(is_open())
