# language_dialog.py
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
import os
from gettext import gettext as _
from gi.repository import Gtk, Granite, Handy

from .config import tessdata_dir
from .language_manager import language_manager


class LanguagePacksDialog(Granite.Dialog):
    def __init__(self, transient_for: Gtk.Window, **kwargs):
        super().__init__(transient_for=transient_for, **kwargs)

        self.resize(400, 450)

        header_label = Granite.HeaderLabel(label=_("Available Languages"), halign=Gtk.Align.CENTER)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        self.main_box.pack_start(header_label, False, True, 8)

        scrolled_view = Gtk.ScrolledWindow(vexpand=True)
        self.language_listbox = Gtk.ListBox()
        self.language_listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        for lang_code in language_manager.get_available_codes():
            self.language_listbox.add(LanguageRow(lang_code))

        scrolled_view.add(self.language_listbox)

        self.main_box.pack_start(scrolled_view, True, True, 8)

        self.get_content_area().add(self.main_box)
        self.add_button(_("OK"), Gtk.ResponseType.OK)

        self.show_all()


class LanguageRow(Gtk.Box):
    def __init__(self, lang_code, **kwargs):
        super().__init__(margin_top=8, margin_bottom=8, **kwargs)

        self.lang_code = lang_code

        self.label = Gtk.Label(_(language_manager.get_language(self.lang_code)), halign=Gtk.Align.START)
        self.spinner = Gtk.Spinner(margin_end=5)

        self.download_widget: Gtk.Button = Gtk.Button()
        self.download_widget.connect('clicked', self.download_clicked)

        self.update_ui()
        self.set_margin_end(12)

    def update_ui(self):
        # Downloaded
        if self.lang_code in language_manager.get_downloaded_codes():
            self.download_widget.set_image(Gtk.Image.new_from_icon_name('user-trash', Gtk.IconSize.BUTTON))
            self.download_widget.set_visible(True)
            self.get_style_context().add_class("downloaded")
            self.spinner.stop()
        # In progress
        elif self.lang_code in language_manager.loading_languages:
            # self.progress.set_visible(True)
            self.spinner.start()
            self.download_widget.set_visible(False)
        # Not yet
        else:
            self.download_widget.set_visible(True)
            self.spinner.stop()
            self.download_widget.set_image(Gtk.Image.new_from_icon_name('folder-download', Gtk.IconSize.BUTTON))

        self.pack_start(self.label, True, True, 8)
        self.pack_end(self.download_widget, False, True, 8)
        self.pack_end(self.spinner, False, True, 8)

    def download_clicked(self, widget) -> None:
        if self.lang_code in language_manager.loading_languages:
            return

        if self.lang_code in language_manager.get_downloaded_codes():
            language_manager.remove_language(self.lang_code)
            self.update_ui()
            return

        language_manager.download(self.lang_code)
        self.update_ui()
