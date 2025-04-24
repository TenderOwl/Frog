# extracted_page.py
#
# Copyright 2021-2025 Andrey Maksimov
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

from gi.repository import Gtk, GObject, Adw
from loguru import logger

from frog.config import RESOURCE_PREFIX
from frog.gobject_worker import GObjectWorker
from frog.services.share_service import ShareService
from frog.services.telemetry import telemetry
from frog.services.tts import ttsservice, TTSService
from frog.settings import Settings
from frog.widgets.share_row import ShareRow


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/extracted_page.ui")
class ExtractedPage(Adw.NavigationPage):
    __gtype_name__ = "ExtractedPage"

    __gsignals__ = {
        "go-back": (GObject.SIGNAL_RUN_LAST, None, (int,)),
        "on-listen-start": (GObject.SIGNAL_RUN_LAST, None, ()),
        "on-listen-stop": (GObject.SIGNAL_RUN_LAST, None, ()),
    }

    # lang_combo: Gtk.MenuButton = Gtk.Template.Child()
    # language_popover: LanguagePopover = Gtk.Template.Child()
    # listen_btn: Gtk.Button = Gtk.Template.Child()
    # listen_cancel_btn: Gtk.Button = Gtk.Template.Child()
    # listen_spinner: Gtk.Spinner = Gtk.Template.Child()
    share_list_box: Gtk.ListBox = Gtk.Template.Child()
    grab_btn: Gtk.Button = Gtk.Template.Child()
    text_copy_btn: Gtk.Button = Gtk.Template.Child()
    text_view: Gtk.TextView = Gtk.Template.Child()
    buffer: Gtk.TextBuffer = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings

        for provider in ShareService.providers():
            self.share_list_box.append(ShareRow(provider))

        ttsservice.connect("stop", self._on_listen_end)

        # self.language_popover.connect('language-changed', self._on_language_changed)

        self.settings = Gtk.Application.get_default().props.settings

        # self.lang_combo.set_label(
        #     language_manager.get_language(self.settings.get_string("active-language"))
        # )

    # def _on_language_changed(self, _: LanguagePopover, language: LanguageItem):
    #     self.lang_combo.set_label(language.title)
    #     self.settings.set_string("active-language", language.code)

    def do_hiding(self) -> None:
        self.buffer.set_text("")
        self.emit("go-back", 1)

    def do_showing(self) -> None:
        telemetry.capture_page_view('extracted')

    @GObject.Property(type=str)
    def extracted_text(self) -> str:
        return self.buffer.get_text(
            start=self.buffer.get_start_iter(),
            end=self.buffer.get_end_iter(),
            include_hidden_chars=False,
        )

    @extracted_text.setter
    def extracted_text(self, text: str):
        try:
            self.buffer.set_text(text)
        except Exception as e:
            logger.debug("Got Exception")
            logger.debug(e)

    def listen(self):
        self.swap_controls(True)

        lang = self.settings.get_string("active-language")

        GObjectWorker.call(
            ttsservice.generate,
            (self.extracted_text, lang[:2]),
            callback=self._on_generated,
        )

    def listen_cancel(self):
        ttsservice.stop_speaking()
        self.swap_controls(False)

    def _on_generated(self, filepath):
        if not filepath:
            self.swap_controls(False)
            return

        ttsservice.play(filepath)

    def _on_listen_end(self, service: TTSService, success: bool):
        self.emit("on-listen-stop")
        self.swap_controls(False)

    def swap_controls(self, state: bool = False):
        pass
        # Stop spinner
        # if state:
        #     self.listen_spinner.start()
        # else:
        #     self.listen_spinner.stop()
        #
        # # Swap buttons
        # self.listen_btn.set_visible(not state)
        # self.listen_cancel_btn.set_visible(state)
