# language_popover_row.py
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

from gi.repository import Gtk, GObject

from frog.config import RESOURCE_PREFIX
from frog.types.language_item import LanguageItem


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/language_popover_row.ui")
class LanguagePopoverRow(Gtk.ListBoxRow):
    __gtype_name__ = 'LanguagePopoverRow'

    lang: LanguageItem

    # Widgets
    title: Gtk.Label = Gtk.Template.Child()
    selection: Gtk.Image = Gtk.Template.Child()

    def __init__(self, lang: LanguageItem):
        super().__init__()
        self.lang = lang
        self.title.set_label(self.lang.title)

        self.lang.bind_property(
            'selected',
            self.selection,
            'visible',
            GObject.BindingFlags.SYNC_CREATE
        )
