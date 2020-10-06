from AppKit import NSWorkspace
active_app_name = NSWorkspace.sharedWorkspace().frontmostApplication().localizedName()
print(active_app_name)
