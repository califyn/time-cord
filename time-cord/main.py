
from AppKit import NSWorkspace
active_app_name = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
print(active_app_name)

# Code credit: kmundnic's answer on https://stackoverflow.com/questions/373020/finding-the-current-active-window-in-mac-os-x-using-python?noredirect=1&lq=1
