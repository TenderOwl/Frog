# language_row.py
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

from gi.repository import Gtk, GLib, GObject
from loguru import logger

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager
from frog.types.language_item import LanguageItem


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/language_row.ui")
class LanguageRow(Gtk.Overlay):
    __gtype_name__ = "LanguageRow"

    label: Gtk.Label = Gtk.Template.Child()
    install_btn: Gtk.Button = Gtk.Template.Child()
    remove_btn: Gtk.Button = Gtk.Template.Child()
    progress_bar: Gtk.ProgressBar = Gtk.Template.Child()
    revealer: Gtk.Revealer = Gtk.Template.Child()

    _item: LanguageItem | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        language_manager.connect("downloading", self.update_progress)
        language_manager.connect("downloaded", self.on_downloaded)

        self.progress_bar.set_fraction(0.14)

        GLib.idle_add(self.update_ui)

    @GObject.Property(type=GObject.TYPE_PYOBJECT)
    def item(self) -> LanguageItem | None:
        return self._item

    @item.setter
    def item(self, item: LanguageItem):
        self._item = item
        self.label.set_label(self._item.title)

    def update_ui(self):
        # English is a default language, therefore, should be no way to remove it
        if self._item.code == "eng":
            self.install_btn.set_visible(False)
            self.remove_btn.set_sensitive(False)
            return

        # Installed
        if self._item.code in language_manager.get_downloaded_codes():
            self.remove_btn.set_visible(True)
        # In progress
        elif self._item.code in language_manager.loading_languages:
            self.install_btn.set_sensitive(False)
        # Not Installed
        else:
            self.install_btn.set_visible(True)
            self.revealer.set_reveal_child(False)

    def update_progress(self, sender, code: str, progress: float) -> None:
        if code == self._item.code:
            GLib.idle_add(self.late_update, code, progress)

    def late_update(self, code, progress):
        if self._item.code == code:
            if not self.revealer.get_reveal_child():
                self.revealer.set_reveal_child(True)

            self.progress_bar.set_fraction(progress / 100)
            self.progress_bar.set_pulse_step(0.05)
            logger.debug(f"Downloading {progress / 100}")

            if progress == 100:
                self.revealer.set_reveal_child(False)

    @Gtk.Template.Callback()
    def _on_download(self, _: Gtk.Button):
        if self._item.code in language_manager.loading_languages:
            return

        language_manager.download(self._item.code)
        self.update_ui()

    @Gtk.Template.Callback()
    def _on_remove(self, _: Gtk.Button):
        if self._item.code in language_manager.loading_languages:
            return

        if self._item.code in language_manager.get_downloaded_codes():
            language_manager.remove_language(self._item.code)
            self.update_ui()

    def on_downloaded(self, sender, code):
        if self._item.code == code:
            GLib.idle_add(self.update_ui)
