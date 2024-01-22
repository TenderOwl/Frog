# language_popover.py
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

from gi.repository import Gtk, Gio, GObject
from loguru import logger

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager
from frog.services.telemetry import telemetry
from frog.settings import Settings
from frog.types.language_item import LanguageItem
from frog.widgets.language_popover_row import LanguagePopoverRow


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/language_popover.ui")
class LanguagePopover(Gtk.Popover):
    __gtype_name__ = "LanguagePopover"

    __gsignals__ = {
        'language-changed': (GObject.SIGNAL_RUN_LAST, None, (LanguageItem,)),
    }

    views: Gtk.Stack = Gtk.Template.Child()
    search_box: Gtk.Box = Gtk.Template.Child()
    entry: Gtk.SearchEntry = Gtk.Template.Child()
    list_view: Gtk.ListBox = Gtk.Template.Child()
    lang_list: Gio.ListStore = Gio.ListStore(item_type=LanguageItem)
    filter_list: Gtk.FilterListModel  # = Gtk.Template.Child()
    filter: Gtk.CustomFilter  # = Gtk.Template.Child()

    settings: Settings
    _active_language: str | None = None

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings

        # Set default language.
        language_manager.connect("downloaded", self._on_language_downloaded)
        language_manager.connect("removed", self._on_language_removed)

        self.active_language = self.settings.get_string('active-language')
        logger.debug("active-language", self.settings.get_string('active-language'))

        # self.populate_model()
        self.bind_model()

        self.connect('show', lambda x: telemetry.capture_page_view('language_popover'))

    def bind_model(self):
        self.filter = Gtk.CustomFilter()
        self.filter.set_filter_func(self._on_language_filter)
        self.filter_list = Gtk.FilterListModel.new(self.lang_list, self.filter)
        self.list_view.bind_model(self.filter_list, LanguagePopoverRow)

    @GObject.Property(type=str)
    def active_lang(self):
        return self._active_language

    @active_lang.setter
    def active_lang(self, lang_code: str):
        self._active_language = lang_code

    def _on_language_filter(self, proposal: LanguageItem, text: str = None) -> bool:
        return not text or text.lower() in proposal.title.lower()

    def _on_language_downloaded(self, _sender, _lang_code: str):
        self.populate_model()

    def _on_language_removed(self, _sender, _lang_code: str):
        self.populate_model()

    @Gtk.Template.Callback()
    def _on_search_activate(self, entry: Gtk.SearchEntry):
        telemetry.capture('language_search activated')
        self._on_language_activate(self.list_view, 0)

    @Gtk.Template.Callback()
    def _on_language_activate(self, _: Gtk.ListBox, row: LanguagePopoverRow):
        item: LanguageItem = row.lang
        self.emit('language-changed', item)
        self.active_language = item.code
        language_manager.active_language = item
        telemetry.capture('language-activated', {'language': self.active_language})
        self.popdown()

    @Gtk.Template.Callback()
    def _on_search_changed(self, entry: Gtk.SearchEntry):
        query = entry.get_text().strip()
        _filter: Gtk.CustomFilter = Gtk.CustomFilter.new(self._on_language_filter, query)
        self.filter_list.set_filter(_filter)
        self.toggle_empty_state(not self.filter_list.get_n_items())

    @Gtk.Template.Callback()
    def _on_stop_search(self, _entry: Gtk.SearchEntry):
        self.popdown()

    @Gtk.Template.Callback()
    def _on_popover_show(self, _):
        self.populate_model()

    @Gtk.Template.Callback()
    def _on_popover_closed(self, *_):
        self.entry.set_text('')

    @Gtk.Template.Callback()
    def _on_add_clicked(self, _: Gtk.Widget):
        self.activate_action('app.preferences')
        self.popdown()

    def populate_model(self):
        self.lang_list.remove_all()

        downloaded_languages = language_manager.get_downloaded_languages(force=True)
        for lang in downloaded_languages:
            code = language_manager.get_language_code(lang)
            self.lang_list.append(LanguageItem(code=code, title=lang, selected=self.active_language == code))

        if self.active_language in language_manager.get_downloaded_codes():
            self.emit('language-changed', language_manager.get_language_item(self.active_language))
        else:
            self.emit('language-changed', language_manager.get_language_item('eng'))

    def toggle_empty_state(self, is_empty: bool = False) -> None:
        if is_empty:
            self.views.set_visible_child_name('empty_page')
        else:
            self.views.set_visible_child_name('languages_page')
