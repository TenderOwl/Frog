# language_dialog.py
#
# Copyright 2021-2022 Andrey Maksimov
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

from gi.repository import Gtk, Gio, GObject

from frog.config import RESOURCE_PREFIX

from .language_manager import language_manager
from .language_row import LanguageRow


class LanguageItem(GObject.GObject):
    title: str
    code: str

    def __init__(self, code: str, title: str):
        GObject.GObject.__init__(self)
        self.title = title
        self.code = code


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/language_dialog.ui')
class LanguagePacksDialog(Gtk.Window):
    __gtype_name__ = 'LanguageDialog'

    downloaded_list = []

    language_listbox: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self, transient_for: Gtk.Window, **kwargs):
        super().__init__(transient_for=transient_for, **kwargs)

        # self.resize(400, 450)
        self.set_modal(True)

        self.store: Gio.ListStore = Gio.ListStore.new(LanguageItem)
        self.model: Gtk.SingleSelection = Gtk.SingleSelection.new(self.store)
        self.language_listbox.bind_model(self.store, create_widget_func=LanguagePacksDialog.create_list_widget)
        self.language_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.reload_language_list()

        language_manager.connect('downloaded', lambda sender, code: self.reload_language_list())
        language_manager.connect('removed', lambda sender, code: self.reload_language_list())

    def reload_language_list(self):
        self.store.remove_all()

        for lang_code in language_manager.get_available_codes():
            self.store.append(LanguageItem(code=lang_code, title=language_manager.get_language(lang_code)))

    @staticmethod
    def create_list_widget(item: LanguageItem):
        row = LanguageRow(item.code, item.title)
        return row

    def sort_rows(self, row1: Gtk.ListBoxRow, row2: Gtk.ListBoxRow) -> int:
        """
        Used to sort languages list by its name not code.

        See https://lazka.github.io/pgi-docs/index.html#Gtk-3.0/callbacks.html#Gtk.ListBoxSortFunc for details.
        """
        # lang_row1: LanguageRow = row1.get_child()
        # lang_row2: LanguageRow = row2.get_child()
        lang1 = language_manager.get_language(row1.lang_code)
        lang2 = language_manager.get_language(row2.lang_code)

        if lang1 > lang2:
            return 1
        elif lang1 < lang2:
            return -1
        return 0
