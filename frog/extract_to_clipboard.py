# extract_to_clipboard.py
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

import re
import time
from gettext import gettext as _
from typing import List

from gi.repository import Gtk, Gio, Gdk, Notify
from gi.repository.GdkPixbuf import Pixbuf

from .config import RESOURCE_PREFIX
from .screenshot_backend import ScreenshotBackend


def extract_to_clipboard(settings: Gio.Settings) -> None:
    """
    Extract the text from the screenshot and copy it directly into the Clipboard.
    """

    # Initialize screenshot backend
    backend = ScreenshotBackend()
    try:
        backend.init_proxy()
    except Exception as e:
        print(e)
        show_notification(_("Failed Attempt"), _("Failed to initialize screenshot service."))
        return

    # get the used languages
    extra_lang = settings.get_string("extra-language")
    active_lang = settings.get_string("active-language")

    language = f"{active_lang}+{extra_lang}"

    # Capture the text
    try:
        text = backend.capture(language)
    except Exception as e:
        print(type(e))
        text = ""

    if not isinstance(text, str) or not text:
        show_notification(_("No text found"))
    else:
        # Copy to Clipboard
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        clipboard.set_text(text, -1)
        clipboard.store()

        url = None
        urls = find_urls(text)
        if urls:
            url = urls[0]

        show_notification(_("Text copied"), clipboard.wait_for_text(), url=url)

    # Wait for the Clipboard to store the text
    time.sleep(1)


def show_notification(title: str, description: str = None, url: str = None) -> None:
    """
    Show a Notification with the Application Logo.
    """
    icon = Pixbuf.new_from_resource_at_scale(
        f"{RESOURCE_PREFIX}/icons/com.github.tenderowl.frog.svg",
        128, 128, True
    )
    notification: Notify.Notification = Notify.Notification.new(summary=title,
                                                                body=description)
    notification.set_icon_from_pixbuf(icon)

    # TODO: make callback works
    # if url:
    #     notification.add_action('clicked', 'Open URL', notification_callback, url)

    notification.show()


def notification_callback(self, notification: Notify.Notification, action_name: str, data: object) -> None:
    print('notification_callback:', action_name)
    Gtk.show_uri_on_window(None, data, Gdk.CURRENT_TIME)


def find_urls(string: str) -> List[str]:
    """
    Search for URL inside given `string` and return list of found urls.
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]
