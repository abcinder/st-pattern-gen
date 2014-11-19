import re
import gtk
import wnck
import time
from pykeyboard import PyKeyboard

k = PyKeyboard()

screen = wnck.screen_get_default()

while gtk.events_pending():
    gtk.main_iteration()

for window in screen.get_windows():
    if re.compile('.*Board.*').match(window.get_name()):
        window.activate(int(time.time()))
        
