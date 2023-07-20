# preferences_general_page.py
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

from gi.repository import Gtk, Adw, Gio

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager
from frog.settings import Settings


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/preferences_general.ui')
class PreferencesGeneralPage(Adw.PreferencesPage):
    __gtype_name__ = 'PreferencesGeneralPage'

    extra_language_combo: Adw.ComboRow = Gtk.Template.Child()
    autocopy_switch: Gtk.Switch = Gtk.Template.Child()
    autolinks_switch: Gtk.Switch = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings

        self.settings.bind('autocopy', self.autocopy_switch, 'active', Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind('autolinks', self.autolinks_switch, 'active', Gio.SettingsBindFlags.DEFAULT)

        downloaded_langs = language_manager.get_downloaded_languages()
        # Fill second language
        self.extra_language_combo.set_model(Gtk.StringList.new(downloaded_langs))
        extra_language_index = downloaded_langs.index(
            language_manager.get_language(self.settings.get_string('extra-language')))
        self.extra_language_combo.set_selected(extra_language_index)
        self.extra_language_combo.connect('notify::selected-item', self._on_extra_language_changed)

    def _on_extra_language_changed(self, combo_row: Adw.ComboRow, _param):
        lang_name = combo_row.get_selected_item().get_string()
        lang_code = language_manager.get_language_code(lang_name)
        print(f'Extra language: {lang_name}:{lang_code}')
        self.settings.set_string('extra-language', lang_code)
