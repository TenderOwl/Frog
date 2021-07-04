# window.py
#
# Copyright 2021 Andrey Maksimov
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
import pytesseract
from gi.repository import Gtk, GdkPixbuf, Gdk, Handy

from lens.config import tessdata_dir_config
from lens.language_model import LanguageModel
from lens.screenshot_backend import ScreenshotBackend, CaptureType


@Gtk.Template(resource_path='/com/github/tenderowl/lens/ui/window.ui')
class LensWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'LensWindow'

    lang_cmb: Gtk.ComboBox = Gtk.Template.Child()
    shot_btn: Gtk.Button = Gtk.Template.Child()
    shot_text: Gtk.TextView = Gtk.Template.Child()
    language_model: Gtk.ListStore = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Handy.init()
        super().__init__(**kwargs)

        self.set_default_size(364, 264)

        self.language_model.append(["eng", "English"])
        self.language_model.append(["rus", "Russian"])

        self.backend = ScreenshotBackend()
        self.shot_btn.connect('clicked', self.on_shot_btn_clicked)

    def on_shot_btn_clicked(self, widget: Gtk.Button) -> None:
        self.get_screenshot()

    def get_screenshot(self):
        position = self
        buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
        # tree_iter = self.lang_cmb.get_active_iter()
        # model = self.lang_model
        # print(model[tree_iter])
        # row_id, name = model[tree_iter][:2]
        text = self.backend.capture(CaptureType=CaptureType.AREA, lang="eng")
        buffer.set_text(text)
