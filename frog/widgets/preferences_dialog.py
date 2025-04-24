# preferences_dialog.py
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

from gi.repository import Gtk, Adw, GObject

from frog.config import RESOURCE_PREFIX
from frog.services.telemetry import telemetry
from frog.widgets.preferences_general_page import PreferencesGeneralPage
from frog.widgets.preferences_languages_page import PreferencesLanguagesPage


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/preferences_dialog.ui')
class PreferencesDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'PreferencesDialog'

    general_page: PreferencesGeneralPage = Gtk.Template.Child()
    languages_page: PreferencesLanguagesPage = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.connect('show', lambda x: telemetry.capture_page_view('preferences'))


class LanguageItem(GObject.GObject):
    title: str
    code: str
    progress: int = 0

    def __init__(self, code: str, title: str):
        GObject.GObject.__init__(self)
        self.title = title
        self.code = code
