# extracted_page.py
#
# Copyright 2021-2023 Andrey Maksimov
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

from gi.repository import Gtk, GObject

from frog.config import RESOURCE_PREFIX
from frog.gobject_worker import GObjectWorker
from frog.services.tts import ttsservice
from frog.settings import Settings


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/extracted_page.ui")
class ExtractedPage(Gtk.Box):
    __gtype_name__ = "ExtractedPage"

    __gsignals__ = {
        'go-back': (GObject.SIGNAL_RUN_LAST, None, (int,)),
        'on-listen-start': (GObject.SIGNAL_RUN_LAST, None, ()),
        'on-listen-stop': (GObject.SIGNAL_RUN_LAST, None, ()),
    }

    back_btn: Gtk.Button = Gtk.Template.Child()
    toolbox: Gtk.Revealer = Gtk.Template.Child()
    grab_btn: Gtk.Button = Gtk.Template.Child()
    text_copy_btn: Gtk.Button = Gtk.Template.Child()
    text_view: Gtk.TextView = Gtk.Template.Child()
    buffer: Gtk.TextBuffer = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings

    @Gtk.Template.Callback()
    def _on_back_btn_clicked(self, _: Gtk.Button) -> None:
        self.buffer.set_text("")
        self.emit('go-back', 1)

    @GObject.Property(type=str)
    def extracted_text(self) -> str:
        return self.buffer.get_text(
            start=self.buffer.get_start_iter(),
            end=self.buffer.get_end_iter(),
            include_hidden_chars=False
        )

    @extracted_text.setter
    def extracted_text(self, text: str):
        self.buffer.set_text(text)

    def listen(self):
        lang = self.settings.get_string('active-language')
        self.emit('on-listen-start')
        GObjectWorker.call(
            ttsservice.speak,
            (self.extracted_text, lang[:2]),
            callback=self._on_listen_end
        )

    def _on_listen_end(self):
        self.emit('on-listen-stop')
