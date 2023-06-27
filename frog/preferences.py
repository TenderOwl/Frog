# preferences.py
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
from gettext import gettext as _

from gi.repository import Gtk, Adw, Gio, GObject

from frog.config import RESOURCE_PREFIX
from .language_dialog import LanguagePacksDialog

from .language_manager import language_manager
from .settings import Settings


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/preferences.ui')
class PreferencesDialog(Adw.PreferencesWindow):
    __gtype_name__ = 'PreferencesWindow'

    settings: Gio.Settings
    general_page: Adw.PreferencesPage
    languages_page: Adw.PreferencesPage
    # languages_list_group: Adw.PreferencesGroup
    installed_languages_list: Gtk.ListBox

    searchbar: Gtk.SearchBar
    language_search_entry: Gtk.SearchEntry
    second_language_combo: Adw.ComboRow
    autocopy_switch: Gtk.Switch
    autolinks_switch: Gtk.Switch

    def __init__(self, settings: Settings, parent: Adw.Window = None):
        super(PreferencesDialog, self).__init__()
        self.settings = settings
        self.set_modal(True)
        self.set_transient_for(parent)

        # Init language model
        self.store: Gio.ListStore = Gio.ListStore.new(LanguageItem)
        self.model: Gtk.FilterListModel = Gtk.FilterListModel.new(self.store, None)
        for lang_code in language_manager.get_available_codes():
            self.store.append(LanguageItem(lang_code, title=language_manager.get_language(lang_code)))

        language_manager.connect('added', self.on_language_added)
        language_manager.connect('downloaded', self.on_language_added)
        language_manager.connect('removed', self.on_language_removed)

        builder = Gtk.Builder()
        builder.add_from_resource(f'{RESOURCE_PREFIX}/ui/preferences_general.ui')
        builder.add_from_resource(f'{RESOURCE_PREFIX}/ui/preferences_languages.ui')

        # General page widgets
        self.general_page = builder.get_object('general_page')
        self.extra_language_combo = builder.get_object('extra_language_combo')
        self.autocopy_switch = builder.get_object('autocopy_switch')
        self.settings.bind('autocopy', self.autocopy_switch, 'state', Gio.SettingsBindFlags.DEFAULT)
        self.autolinks_switch = builder.get_object('autolinks_switch')
        self.settings.bind('autolinks', self.autolinks_switch, 'state', Gio.SettingsBindFlags.DEFAULT)

        downloaded_langs = language_manager.get_downloaded_languages()
        # Fill second language
        self.extra_language_combo.set_model(Gtk.StringList.new(downloaded_langs))
        extra_language_index = downloaded_langs.index(
            language_manager.get_language(settings.get_string('extra-language')))
        self.extra_language_combo.set_selected(extra_language_index)
        self.extra_language_combo.connect('notify::selected-item', self.on_extra_language_changed)

        # Language page widgets
        self.searchbar = builder.get_object('search_revealer')
        self.language_search_entry = builder.get_object('language_search_entry')
        self.languages_page = builder.get_object('languages_page')
        self.installed_languages_list = builder.get_object('installed_languages_list')

        # self.installed_switch.connect('notify::active', self.on_installed_switched)
        self.language_search_entry.connect('search-changed', self.on_language_search)
        self.language_search_entry.connect('stop-search', self.on_language_search_stop)
        self.searchbar.connect('notify::search-mode-enabled', self.on_search_mode_enabled)

        self.add(self.general_page)
        self.add(self.languages_page)

        self.installed_languages_list.bind_model(self.model, LanguagePacksDialog.create_list_widget)
        self.installed_languages_list.connect('row-activated', self.langs_list_row_activated)

        # Append "view more" button to the end of the language list
        self.add_view_more_langs()
        self.activate_filter()

    def add_view_more_langs(self) -> None:
        view_more_langs_row = Gtk.ListBoxRow(tooltip_text=_('View all available languages'))
        view_more_image: Gtk.Image = Gtk.Image.new_from_icon_name('view-more-symbolic')
        view_more_image.set_margin_top(14)
        view_more_image.set_margin_bottom(14)
        view_more_langs_row.set_child(view_more_image)

        self.installed_languages_list.append(view_more_langs_row)

    @property
    def is_search_mode(self):
        return self.searchbar.get_search_mode()

    def langs_list_row_activated(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow, user_data: dict = None) -> None:
        if row.get_index() == self.model.get_n_items():
            if not self.is_search_mode:
                self.deactivate_filter()
                self.searchbar.set_search_mode(True)
                self.language_search_entry.grab_focus()
            else:
                self.activate_filter()
                self.searchbar.set_search_mode(False)

    def activate_filter(self, search_text: str = None) -> None:
        _filter: Gtk.CustomFilter = Gtk.CustomFilter.new(PreferencesDialog.filter_func, search_text)
        self.model.set_filter(_filter)

    def deactivate_filter(self):
        self.model.set_filter(None)

    def on_language_search(self, entry: Gtk.SearchEntry, user_data: object = None) -> None:
        self.activate_filter(entry.get_text())

    def on_language_search_stop(self, entry: Gtk.SearchEntry) -> None:
        entry.set_text('')
        self.searchbar.set_search_mode(False)
        self.activate_filter()

    def on_search_mode_enabled(self, searchbar, enabled: bool) -> None:
        if not self.searchbar.get_search_mode():
            self.activate_filter()

    @staticmethod
    def filter_func(item, user_data: str) -> bool:
        if user_data:
            return user_data.lower() in item.title.lower()
        else:
            return item.code in language_manager.get_downloaded_codes()

    def on_language_added(self, _sender, _code: str = None) -> None:
        if not self.searchbar.get_search_mode():
            self.activate_filter()

    def on_language_removed(self, _sender, _code) -> None:
        if not self.searchbar.get_search_mode():
            self.activate_filter()

    def on_extra_language_changed(self, combo_row: Adw.ComboRow, _param) -> None:
        lang_name = combo_row.get_selected_item().get_string()
        lang_code = language_manager.get_language_code(lang_name)
        print(f'Extra language: {lang_name}:{lang_code}')
        self.settings.set_string('extra-language', lang_code)


class LanguageItem(GObject.GObject):
    title: str
    code: str
    progress: int = 0

    def __init__(self, code: str, title: str):
        GObject.GObject.__init__(self)
        self.title = title
        self.code = code
