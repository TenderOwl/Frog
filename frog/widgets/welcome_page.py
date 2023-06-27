# welcome_page.py
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

from gi.repository import Adw
from gi.repository import Gtk, Gdk

from frog.config import RESOURCE_PREFIX, APP_ID
from frog.language_manager import language_manager
from frog.types.language_item import LanguageItem
from frog.widgets.language_popover import LanguagePopover


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/welcome_page.ui")
class WelcomePage(Gtk.Box):
    __gtype_name__ = "WelcomePage"

    spinner: Gtk.Spinner = Gtk.Template.Child()
    lang_combo: Gtk.MenuButton = Gtk.Template.Child()
    welcome: Adw.StatusPage = Gtk.Template.Child()
    language_popover: LanguagePopover = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        logo = Gdk.Texture.new_from_resource(f"{RESOURCE_PREFIX}/icons/{APP_ID}.svg")
        self.welcome.set_paintable(logo)

        self.language_popover.connect('language-changed', self._on_language_changed)

        self.settings = Gtk.Application.get_default().props.settings

        self.lang_combo.set_label(
            language_manager.get_language(self.settings.get_string("active-language"))
        )

    def _on_language_changed(self, _: LanguagePopover, language: LanguageItem):
        self.lang_combo.set_label(language.title)
        self.settings.set_string("active-language", language.code)
