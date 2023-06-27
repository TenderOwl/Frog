# language_row.py
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

from gi.repository import Gtk, GLib

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/language_row.ui')
class LanguageRow(Gtk.Overlay):
    __gtype_name__ = 'LanguageRow'

    label: Gtk.Label = Gtk.Template.Child()
    download_widget: Gtk.Button = Gtk.Template.Child()
    progress_bar: Gtk.ProgressBar = Gtk.Template.Child()
    revealer: Gtk.Revealer = Gtk.Template.Child()

    def __init__(self, lang_code, lang_title, **kwargs):
        super().__init__(**kwargs)

        self.lang_code = lang_code
        self.lang_title = lang_title

        self.download_widget.connect('clicked', self.download_clicked)
        language_manager.connect('downloading', self.update_progress)
        language_manager.connect('downloaded', self.on_downloaded)

        self.label.set_label(self.lang_title)
        self.progress_bar.set_fraction(0.14)

        GLib.idle_add(self.update_ui)

    def update_ui(self):
        # English is a default language, therefore, should be no way to remove it
        if self.lang_code == "eng":
            self.download_widget.set_icon_name('user-trash-symbolic')
            self.download_widget.set_sensitive(False)
            return

        # Downloaded
        if self.lang_code in language_manager.get_downloaded_codes():
            self.download_widget.set_icon_name('user-trash-symbolic')
            self.download_widget.set_sensitive(True)
        # In progress
        elif self.lang_code in language_manager.loading_languages:
            self.download_widget.set_sensitive(False)
        # Not yet
        else:
            self.download_widget.set_icon_name('folder-download-symbolic')
            self.download_widget.set_sensitive(True)
            self.revealer.set_reveal_child(False)

    def update_progress(self, sender, code: str, progress: float) -> None:
        if code == self.lang_code:
            GLib.idle_add(self.late_update, code, progress)

    def late_update(self, code, progress):
        if self.lang_code == code:
            if not self.revealer.get_reveal_child():
                self.revealer.set_reveal_child(True)

            self.progress_bar.set_fraction(progress / 100)
            self.progress_bar.set_pulse_step(0.05)
            print(f'Downloading {progress / 100}')

            if progress == 100:
                self.revealer.set_reveal_child(False)

    def download_clicked(self, widget: Gtk.Button) -> None:
        if self.lang_code in language_manager.loading_languages:
            return

        if self.lang_code in language_manager.get_downloaded_codes():
            language_manager.remove_language(self.lang_code)
            self.update_ui()
            return

        language_manager.download(self.lang_code)
        self.update_ui()

    def on_downloaded(self, sender, code):
        if self.lang_code == code:
            GLib.idle_add(self.update_ui)
