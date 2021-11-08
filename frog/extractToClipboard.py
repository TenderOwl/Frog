# extractToClipboard.py
#
# Copyright 2021 FilePhil
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.

from gettext import gettext as _

from gi.overrides.GdkPixbuf import Pixbuf
from gi.repository import Gtk, Handy, Gio, Gdk, GLib, Granite
from gi.repository import Notify

from .config import RESOURCE_PREFIX
from .screenshot_backend import ScreenshotBackend



import time

def get_shortcut_text(settings: Gio.Settings) -> None:
    """ Extract the text from the screenshot and copy it directly into the Clipboad."""

    # Initialize screenshot backend
    backend = ScreenshotBackend()

    # get the used languges
    extra_lang = settings.get_string("extra-language")
    active_lang =  settings.get_string("active-language")

    languge  = f'{active_lang}+{extra_lang}'

    # Capture the text
    try:
        text = backend.capture(languge)

    except Exception as e:
        text = ""

    if text=="" or type(text) != str:
        Notify.init("No Text found")
        notification = Notify.Notification.new("")
    else:
        # Copy to Clipboard
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        clipboard.set_text(text,-1)
        clipboard.store()

        Notify.init("Text copied")
        notification = Notify.Notification.new(clipboard.wait_for_text())

    icon = Pixbuf.new_from_resource_at_scale(
        f'{RESOURCE_PREFIX}/icons/com.github.tenderowl.frog.svg',
        128, 128, True
    )
    notification.set_icon_from_pixbuf(icon)
    notification.show()
    # Wait for the Clipboard to store the text
    time.sleep(1)
