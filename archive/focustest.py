import platform
if platform.system() == "Darwin":
    from AppKit import NSApp

def callback(target, button, time, *args):
    if platform.system() == "Darwin":
        NSApp.activateIgnoringOtherApps_(True)
    menu.popup(None,None, None, button, time)
...
icon.connect("popup-menu", callback)
window.show_all()
if platform.system() == "Darwin":
    NSApp.activateIgnoringOtherApps_(True)
