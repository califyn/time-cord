from subprocess import Popen, PIPE
from PIL import Image, ImageGrab
import time, platform, ssl, requests
import easyocr
import numpy

requests.packages.urllib3.disable_warnings()

# ---------------------------------------------------------- #
# The SSL lib threw a bunch of errors when I ran it
# There's no need to perform a rigorous ssl origin check on the download req.
# ---------------------------------------------------------- #

try:
    _unvf_contxt = ssl._create_unverified_context
except AttributeError:
    pass

ssl._create_default_https_context = _unvf_contxt

# ---------------------------------------------------------- #

if platform.system() == "Windows":
    """
    Windows-only imports; these will fail on MacOS
    """
    import win32process
    import wmi
    import win32gui

class UnsupportedOSError(Exception):
    """
    Handles the case of users running on Windows/Linux.
    """

class Monitor():
    def __init__(*args, **kwargs):
        self = args[0]
        self.ocr = easyocr.Reader(['en']) # need to run only once to load model into memory)
        self.debug = False

        for arg in kwargs:
            if arg == "debug":
                self.debug = kwargs[arg]

    def return_top(self):
        """
        Return name and title of the focused window in string format in supported OSes.

        Code adapted from: Albert's answer (https://stackoverflow.com/questions/5292204/macosx-get-foremost-window-title)
            and RobC's answer (https://stackoverflow.com/questions/51775132/how-to-get-return-value-from-applescript-in-python)

        Outputs:
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

    def channel_name(self):
        """
        Determine if Discord is open in the top window, and return current channel name if so.

        Outputs:
          str: channel_name if Discord is open, else None
        """

        top = self.return_top()
        if top[0:8] == "Discord,":
            hash = top.find("#")
            if hash == -1:
                hash = top.index("@")
            top = top[hash + 1:]
            space = top.index(" ")
            top = top[:space]
            return top
        else:
            return None

    def get_bounds(self, process="Discord"):
        """
        Get the boundaries of a window corresponding to a specified application/process.
        It is necessary said window is visible on the computer desktop.

        Inputs:
            process: A string which is the name of the application that you want bounds of

        Outputs:
            int, int, int, int: Four coordinates corresponding to the bounds of the process.
        """

        if platform.system() == "Darwin":
            size_position = '''
                global s, p
                tell application "System Events"
    	           tell application process "Discord"
    		             set s to size of window 1
    		             set p to position of window 1
    	            end tell
                end tell
                return {s, p}
              '''

            proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            bounds, error = proc.communicate(size_position)
            sp_arr = bounds[:-1].split(",")
            for i in range(0, len(sp_arr)):
                sp_arr[i] = int(sp_arr[i])
            coords = [0, 0, 0, 0]
            coords[0] = sp_arr[2]
            coords[1] = sp_arr[3]
            coords[2] = sp_arr[2] + sp_arr[0]
            coords[3] = sp_arr[3] + sp_arr[1]
            return coords
        elif platform.system() == "Windows":
            if self.debug:
                print("Todo...")
            # TODO: same function for Windows
            # NOTE bounds are [x_1, x_2, y_1, y_2]
        else:
            raise UnsupportedOSError(platform.system() + " is not supported by this version of time-cord.")


    def get_screenshot(self, process="Discord"):
        """
        Get a screenshot of a window corresponding to an application/process which is current in the display.

        Inputs:
            process: A string which is the name of the application which will be screenshotted

        Outputs:
            Image: a picture of the application.
        """

        ss = ImageGrab.grab(bbox=self.get_bounds(process))
        return ss

    def server_name(self):
        """
        Calculates the server name of the open Discord window.

        Outputs:
            str: Name of the server.
        """

        ss = self.get_screenshot()
        # Get server text area bounding box (using colors)
        px = ss.load()
        left = 6
        if self.debug:
            print(px[6, 0])
            print(list(px[left, 0]))
        if px[left, 0][0] == 47 and px[left, 0][1] == 49 and px[left, 0][2] == 55:
            return "Settings"
        if px[left, 0][0] == 242 and px[left, 0][1] == 243 and px[left, 0][2] == 245:
            return "Settings"
        while px[left, 0][0] == 32 and px[left, 0][1] == 34 and px[left, 0][2] == 37:
            left = left + 1
        while px[left, 0][0] == 227 and px[left, 0][1] == 229 and px[left, 0][2] == 233:
            left = left + 1
        if left == 6:
            raise Exception("Didn't take a screenshot of Discord")
        top = 0
        while (px[left, top][0] != 47 or px[left, top][1] != 49 or px[left, top][2] != 55) and (px[left, top][0] != 242 or px[left, top][1] != 243 or px[left, top][2] != 245):
            top = top + 1
        right = left
        while px[right, top][0] == 47 and px[right, top][1] == 49 and px[right, top][2] == 55:
            right = right + 1
        while px[right, top][0] == 242 and px[right, top][1] == 243 and px[right, top][2] == 245:
            right = right + 1
        bottom = top
        while px[left, bottom][0] == 47 and px[left, bottom][1] == 49 and px[left, bottom][2] == 55:
            bottom = bottom + 1
        while px[left, bottom][0] == 242 and px[left, bottom][1] == 243 and px[left, bottom][2] == 245:
            bottom = bottom + 1
        if self.debug:
            print(str(top) + ", " + str(bottom) + ", " + str(left) + ", " + str(right))
        # Check if we're in DMs
        hmiddle = (left + right) // 2
        for i in range(top + 1, bottom - 1):
            if px[hmiddle, i][0] == 32 or px[hmiddle, i][0] == 227:
                if self.debug:
                    print(str(i))
                return "DMs"
        # Otherwise, get server name
        server = ss.crop((left, top, right, bottom))
        name = self.ocr.readtext(numpy.array(server))
        return name[0][1]
