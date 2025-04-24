# share_service.py
#
# Copyright 2025 Andrey Maksimov
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
from typing import List
from urllib.parse import quote

from gi.repository import GObject, Gtk
from loguru import logger

from frog.services.telemetry import telemetry


class ShareService(GObject.GObject):
    __gtype_name__ = "ShareService"

    __gsignals__ = {"share": (GObject.SIGNAL_RUN_LAST, None, (bool,))}

    launcher: Gtk.UriLauncher = Gtk.UriLauncher()

    def __init__(self):
        super().__init__()

    @staticmethod
    def providers() -> List[str]:
        return [
            "email",
            "mastodon",
            "pocket",
            "instapaper",
            "reddit",
            "twitter",
            "telegram",
        ]

    def share(self, provider: str, text: str):
        telemetry.capture("share", {'provider': provider})
        if not text:
            return

        text = text.strip()
        if handler := getattr(self, f"get_link_{provider}"):
            try:
                share_link: str = handler(quote(text))
                self.launcher.set_uri(share_link)
                self.launcher.launch(callback=self._on_share)
            except Exception as e:
                logger.debug(f"ERROR: failed to share, error: {e}")

    def _on_share(self, _, result):
        self.emit("share", self.launcher.launch_finish(result))

    @staticmethod
    def get_link_telegram(text: str):
        return f"tg://msg_url?url={text}"

    @staticmethod
    def get_link_reddit(text: str):
        return f"https://www.reddit.com/submit?title={text}"

    @staticmethod
    def get_link_mastodon(text: str):
        return f"https://sharetomastodon.github.io/?title={text}"

    @staticmethod
    def get_link_twitter(text: str):
        return f"https://twitter.com/intent/tweet?text={text}"

    @staticmethod
    def get_link_instapaper(text: str):
        return f"https://www.instapaper.com/hello2?text={text}"

    @staticmethod
    def get_link_pocket(text: str):
        return f"https://getpocket.com/save?text={text}"

    @staticmethod
    def get_link_email(text: str):
        return f"mailto:?body={text}"
