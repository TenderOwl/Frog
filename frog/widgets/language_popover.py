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

from gettext import gettext as _

from gi.repository import Gtk, Gdk, Gio, GObject, GLib

from frog.config import RESOURCE_PREFIX
from frog.types.language_item import LanguageItem
from frog.language_manager import language_manager


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/language_popover.ui")
class LanguagePopover(Gtk.Popover):
    __gtype_name__ = "LanguagePopover"

    __gsignals__ = {
        'language-changed': (GObject.SIGNAL_RUN_LAST, None, (LanguageItem,)),
    }

    entry: Gtk.SearchEntry = Gtk.Template.Child()
    list_view: Gtk.ListView = Gtk.Template.Child()
    list_store: Gio.ListStore = Gtk.Template.Child()

    _active_language: str | None = 'English'

    def __init__(self):
        super().__init__()

        # Set default language.
        language_manager.connect('downloading', self._on_language_downloading)
        language_manager.connect("downloaded", self._on_language_downloaded)
        language_manager.connect("removed", self._on_language_removed)

        self.fill_lang_combo()
        if not language_manager.get_downloaded_codes():
            self.text_shot_btn.set_sensitive(False)

    @GObject.Property(type=str)
    def active_lang(self):
        return self._active_language

    @active_lang.setter
    def active_lang(self, lang_code: str):
        self._active_language = lang_code

    def _on_language_downloading(self, sender, lang_code: str):
        print(f"on_language_downloading: {lang_code}")
        self.spinner.start()

    def _on_language_downloaded(self, sender, lang_code: str):
        language = language_manager.get_language(lang_code)
        print("on_language_downloaded: " + language)
        self.show_toast(_(f"{language} language downloaded."))
        self.fill_lang_combo()

        if not language_manager.loading_languages:
            self.spinner.stop()

    def _on_language_removed(self, sender, lang_code: str):
        print("on_language_removed: " + lang_code)
        self.fill_lang_combo()

    @Gtk.Template.Callback()
    def _on_key_event_pressed(self,
                              controller: Gtk.EventController,
                              keyval,
                              keycode,
                              state: Gdk.ModifierType, *_):
        print("key pressed", keycode)

    @Gtk.Template.Callback()
    def _on_factory_setup(self, _: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        label = Gtk.Label(margin_top=8, margin_end=8,
                          margin_start=8, margin_bottom=8,
                          xalign=0)
        list_item.set_child(label)

    @Gtk.Template.Callback()
    def _on_factory_bind(self, _: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        row: Gtk.Label = list_item.get_child()  # type: ignore
        item: LanguageItem = list_item.get_item()  # type: ignore
        row.set_label(item.title)

    @Gtk.Template.Callback()
    def _on_language_activate(self, _: Gtk.ListView, position: int):
        item = self.list_store.get_item(position)
        self.emit('language-changed', item)
        language_manager.active_language = item
        self.popdown()

    def fill_lang_combo(self):
        self.list_store.remove_all()

        downloaded_languages = language_manager.get_downloaded_languages(force=True)
        for lang in downloaded_languages:
            GLib.idle_add(
                self.list_store.append,
                LanguageItem(code=language_manager.get_language_code(lang), title=lang),
                priority=GLib.PRIORITY_LOW
            )

        # self.emit('language-changed', 'English')
        # self.lang_combo.set_label(_("English"))

        if self._active_language in language_manager.get_downloaded_codes():
            # self.lang_combo.set_label(language_manager.get_language(self.active_lang))

            self.emit('language-changed', language_manager.get_language_item(self._active_language))
        else:
            self.emit('language-changed', language_manager.get_language_item('eng'))
            # self.lang_combo.set_label(_("English"))
