# preferences_languages_page.py
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

from gi.repository import Gtk, Adw, Gio

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager
from frog.settings import Settings
from frog.types.language_item import LanguageItem
from frog.widgets.language_row import LanguageRow


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/preferences_languages.ui')
class PreferencesLanguagesPage(Adw.PreferencesPage):
    __gtype_name__ = 'PreferencesLanguagesPage'

    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    language_search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    list_view: Gtk.ListView = Gtk.Template.Child()
    model: Gtk.FilterListModel = Gtk.Template.Child()
    list_store: Gio.ListStore = Gtk.Template.Child()
    revealer: Gtk.Revealer = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings

        # self.store: Gio.ListStore = Gio.ListStore.new(LanguageItem)
        # self.model: Gtk.FilterListModel = Gtk.FilterListModel.new(self.store, None)
        for lang_code in language_manager.get_available_codes():
            self.list_store.append(LanguageItem(lang_code, title=language_manager.get_language(lang_code)))

        language_manager.connect('added', self.on_language_added)
        language_manager.connect('downloaded', self.on_language_added)
        language_manager.connect('removed', self.on_language_removed)

        # self.installed_switch.connect('notify::active', self.on_installed_switched)
        self.language_search_entry.connect('search-changed', self.on_language_search)
        self.language_search_entry.connect('stop-search', self.on_language_search_stop)
        self.search_bar.connect('notify::search-mode-enabled', self.on_search_mode_enabled)

        self.load_languages()
        self.activate_filter()

    @Gtk.Template.Callback()
    def _on_item_setup(self, factory: Gtk.SignalListItemFactory, item: Gtk.ListItem):
        row: LanguageRow = LanguageRow()
        item.set_child(row)

    @Gtk.Template.Callback()
    def _on_item_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem):
        row: LanguageRow = list_item.get_child()
        item: LanguageItem = list_item.get_item()
        row.item = item

    @Gtk.Template.Callback()
    def _on_add_language(self, sender: Gtk.Widget):
        if not self.is_search_mode:
            self.deactivate_filter()
            self.search_bar.set_search_mode(True)
            self.language_search_entry.grab_focus()
        else:
            self.activate_filter()
            self.search_bar.set_search_mode(False)

    def load_languages(self):
        self.list_store.remove_all()
        for lang_code in language_manager.get_available_codes():
            self.list_store.append(language_manager.get_language_item(lang_code))

    def add_view_more_langs(self) -> None:
        view_more_langs_row = Gtk.ListBoxRow(tooltip_text=_('View all available languages'))
        view_more_image: Gtk.Image = Gtk.Image.new_from_icon_name('view-more-symbolic')
        view_more_image.set_margin_top(14)
        view_more_image.set_margin_bottom(14)
        view_more_langs_row.set_child(view_more_image)

        self.list_store.append(view_more_langs_row)

    @property
    def is_search_mode(self):
        return self.search_bar.get_search_mode()

    def activate_filter(self, search_text: str = None) -> None:
        _filter: Gtk.CustomFilter = Gtk.CustomFilter.new(PreferencesLanguagesPage.filter_func, search_text)
        self.model.set_filter(_filter)

    def deactivate_filter(self):
        self.model.set_filter(None)

    def on_language_search(self, entry: Gtk.SearchEntry, _user_data: object = None) -> None:
        self.activate_filter(entry.get_text())

    def on_language_search_stop(self, entry: Gtk.SearchEntry) -> None:
        entry.set_text('')
        self.search_bar.set_search_mode(False)
        self.revealer.set_reveal_child(True)
        self.activate_filter()

    def on_search_mode_enabled(self, _searchbar, _enabled: bool) -> None:
        if not self.search_bar.get_search_mode():
            self.activate_filter()

    @staticmethod
    def filter_func(item, user_data: str) -> bool:
        if user_data:
            return user_data.lower() in item.title.lower()
        else:
            return item.code in language_manager.get_downloaded_codes()

    def on_language_added(self, _sender, _code: str = None) -> None:
        if not self.search_bar.get_search_mode():
            self.activate_filter()

    def on_language_removed(self, _sender, _code) -> None:
        if not self.search_bar.get_search_mode():
            self.activate_filter()
