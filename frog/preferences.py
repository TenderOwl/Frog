# preferences.py
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
from gettext import gettext as _

from gi.repository import Gtk, Adw, Gdk, Gio, GObject

from frog.config import RESOURCE_PREFIX
from .language_dialog import LanguagePacksDialog

from .language_manager import language_manager


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/preferences.ui')
class PreferencesDialog(Adw.PreferencesWindow):
    __gtype_name__ = 'PreferencesWindow'

    general_page: Adw.PreferencesPage
    languages_page: Adw.PreferencesPage
    installed_languages_list: Gtk.ListBox
    installed_switch: Gtk.Switch

    def __init__(self, parent: Adw.Window = None):
        super(PreferencesDialog, self).__init__()
        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_default_size(480, 400)

        builder = Gtk.Builder()
        builder.add_from_resource(f'{RESOURCE_PREFIX}/ui/preferences_general.ui')
        builder.add_from_resource(f'{RESOURCE_PREFIX}/ui/preferences_languages.ui')

        self.general_page = builder.get_object('general_page')
        self.languages_page = builder.get_object('languages_page')
        self.installed_switch = builder.get_object('installed_switch')
        self.installed_switch.connect('activate', self.on_installed_switched)
        self.installed_languages_list = builder.get_object('installed_languages_list')

        self.add(self.general_page)
        self.add(self.languages_page)

        self.store: Gio.ListStore = Gio.ListStore.new(LanguageItem)
        self.model: Gtk.SingleSelection = Gtk.SortListModel.new(self.store)
        self.installed_languages_list.bind_model(self.model, LanguagePacksDialog.create_list_widget)

        for lang_code in language_manager.get_available_codes():
            self.store.append(LanguageItem(lang_code, title=language_manager.get_language(lang_code)))

    def on_installed_switched(self, sender, event):
        print('on_installed_switched')


class LanguageItem(GObject.GObject):
    title: str
    code: str
    progress: int = 0

    def __init__(self, code: str, title: str):
        GObject.GObject.__init__(self)
        self.title = title
        self.code = code
