# main.py
#
# Copyright 2021 Andrey Maksimov
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

import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('Handy', '1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, Gio, Granite, GObject, GLib
from .settings import Settings
from .window import FrogWindow
from .extract_to_clipboard import  get_shortcut_text


class Application(Gtk.Application):
    granite_settings: Granite.Settings
    gtk_settings: Gtk.Settings

    def __init__(self):
        super().__init__(application_id='com.github.tenderowl.frog',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        # Init GSettings
        self.settings = Settings.new()

        # create command line option entries
        shortcut_entry = GLib.OptionEntry()
        shortcut_entry.long_name = 'extract_to_clipboard'
        shortcut_entry.short_name = ord('e')
        shortcut_entry.flags = 0
        shortcut_entry.arg = GLib.OptionArg.NONE
        shortcut_entry.arg_date = None
        shortcut_entry.description = _('Extract directly into the clipboard')
        shortcut_entry.arg_description = None

        self.add_main_option_entries([shortcut_entry])

    def do_activate(self):

        self.granite_settings = Granite.Settings.get_default()
        self.gtk_settings = Gtk.Settings.get_default()

        # Then, we check if the user's preference is for the dark style and set it if it is
        self.gtk_settings.props.gtk_application_prefer_dark_theme = \
            self.granite_settings.props.prefers_color_scheme == Granite.SettingsColorScheme.DARK

        # Finally, we listen to changes in Granite.Settings and update our app if the user changes their preference
        self.granite_settings.connect("notify::prefers-color-scheme",
                                      self.color_scheme_changed)

        win = self.props.active_window
        if not win:
            win = FrogWindow(settings=self.settings, application=self)
        win.present()

    def color_scheme_changed(self, _old, _new):
        self.gtk_settings.props.gtk_application_prefer_dark_theme = \
            self.granite_settings.props.prefers_color_scheme == Granite.SettingsColorScheme.DARK

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()

        if options.contains("extract_to_clipboard"):
            get_shortcut_text(self.settings)
            return 0

        self.activate()
        return 0

def main(version):
    app = Application()
    return app.run(sys.argv)
