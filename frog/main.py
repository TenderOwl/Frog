# main.py
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

import datetime
import sys
from gettext import gettext as _

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Notify', '0.7')
gi.require_version('Xdp', '1.0')

from gi.repository import Gtk, Gio, GLib, Notify, Adw, GdkPixbuf, Gdk
from .clipboard_service import clipboard_service
from .config import RESOURCE_PREFIX
from .language_manager import language_manager
from .screenshot_backend import ScreenshotBackend
from .settings import Settings
from .window import FrogWindow


class Application(Adw.Application):
    gtk_settings: Gtk.Settings

    def __init__(self, version=None):
        super().__init__(application_id='com.github.tenderowl.frog',
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.backend = None
        self.version = version

        # Init GSettings
        self.settings = Settings.new()

        self.add_main_option(
            'extract_to_clipboard',
            ord('e'),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            _('Extract directly into the clipboard'),
            None
        )

        # Initialize tesseract data files storage.
        language_manager.init_tessdata()

        # Initialize libnotify.
        Notify.init("Frog")

    def do_startup(self, *args, **kwargs):
        Adw.Application.do_startup(self)

        # create command line option entries
        shortcut_entry = GLib.OptionEntry()
        shortcut_entry.long_name = 'extract_to_clipboard'
        shortcut_entry.short_name = ord('e')
        shortcut_entry.flags = 0
        shortcut_entry.arg = GLib.OptionArg.NONE
        shortcut_entry.arg_date = None
        shortcut_entry.description = _('Extract directly into the clipboard')
        shortcut_entry.arg_description = None

        self.backend = ScreenshotBackend()
        self.backend.connect('decoded', Application.on_decoded)

        shot_action: Gio.SimpleAction = Gio.SimpleAction.new(name="get_screenshot", parameter_type=None)
        shot_action.connect("activate", self.get_screenshot)
        self.add_action(shot_action)
        self.set_accels_for_action("app.get_screenshot", ("<Control>g",))

        copy_action: Gio.SimpleAction = Gio.SimpleAction.new(name="copy_to_clipboard", parameter_type=None)
        copy_action.connect("activate", self.on_copy_to_clipboard)
        self.add_action(copy_action)
        self.set_accels_for_action("app.copy_to_clipboard", ("<Control>c",))

        shot_action_and_copy: Gio.SimpleAction = Gio.SimpleAction.new(name="get_screenshot_and_copy",
                                                                      parameter_type=None)
        shot_action_and_copy.connect("activate", self.get_screenshot_and_copy)
        self.add_action(shot_action_and_copy)
        self.set_accels_for_action("app.get_screenshot_and_copy", ("<Control><Shift>g",))

        action = Gio.SimpleAction.new("preferences", None)
        action.connect("activate", self.on_preferences)
        self.add_action(action)
        self.set_accels_for_action("app.preferences", ("<Control>comma",))

        action = Gio.SimpleAction.new("open_image", None)
        action.connect("activate", self.open_image)
        self.add_action(action)
        self.set_accels_for_action("app.open_image", ("<Control>o",))

        action = Gio.SimpleAction.new("show_uri", GLib.VariantType.new('s'))
        action.connect("activate", self.on_show_uri)
        self.add_action(action)

        action = Gio.SimpleAction.new("shortcuts", None)
        action.connect("activate", self.on_shortcuts)
        self.add_action(action)
        self.set_accels_for_action("app.shortcuts", ("<Control>question",))

        action = Gio.SimpleAction.new(name="about", parameter_type=None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new(name="quit", parameter_type=None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        self.set_accels_for_action("app.quit", ("<Control>q",))

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = FrogWindow(settings=self.settings, application=self)
        win.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if "extract_to_clipboard" in options:
            self.backend.capture(self.settings.get_string("active-language"), True)
            return 1

        self.activate()
        return 0

    def on_preferences(self, _action, _param) -> None:
        self.get_active_window().show_preferences()

    def on_about(self, _action, _param):
        about_window = Adw.AboutWindow(
            application_name="Frog",
            application_icon="com.github.tenderowl.frog",
            version=self.version,
            copyright=f'© {datetime.date.today().year} Tender Owl',
            website="https://getfrog.app",
            issue_url="https://github.com/TenderOwl/Frog/issues/new",
            license_type=Gtk.License.MIT_X11,
            developer_name="TenderOwl Team",
            developers=["Andrey Maksimov"],
            release_notes="""<p>In this update, we've made a number of improvements to our app.</p>
                <ul>
                    <li>We have redesigned the settings dialog to make it more user-friendly and understandable.</li>
                    <li>Now you can easily find the language you want by searching.</li>
                    <li>In addition, we have added the ability to select a second language for extracting text from images.</li>
                    <li>The Frog can automatically follow links extracted from QR codes.</li>
                    <li>We also updated the localization and improved the overall performance of the app.</li>
                    <li>Fixed some bugs and bugs.</li>
                </ul>
                <p>We hope you enjoy our work!</p>
            """,
            transient_for=self.props.active_window
        )
        about_window.present()

    def on_quit(self, _action, _param):
        self.quit()

    def on_shortcuts(self, _action, _param):
        builder = Gtk.Builder()
        builder.add_from_resource(f"{RESOURCE_PREFIX}/ui/shortcuts.ui")
        builder.get_object("shortcuts").set_transient_for(self.get_active_window())
        builder.get_object("shortcuts").present()

    def on_copy_to_clipboard(self, _action, _param) -> None:
        self.get_active_window().on_copy_to_clipboard(self)

    def on_show_uri(self, _action, param) -> None:
        Gtk.show_uri(None, param.get_string(), Gdk.CURRENT_TIME)

    def get_screenshot(self, _action, _param) -> None:
        self.get_active_window().get_screenshot()

    def get_screenshot_and_copy(self, _action, _param) -> None:
        self.get_active_window().get_screenshot(copy=True)

    def open_image(self, _action, _param) -> None:
        self.get_active_window().open_image()

    @staticmethod
    def on_decoded(_sender, text: str, copy: bool) -> None:
        icon = GdkPixbuf.Pixbuf.new_from_resource_at_scale(
            f"{RESOURCE_PREFIX}/icons/com.github.tenderowl.frog.svg",
            128, 128, True
        )

        if not text:
            notification: Notify.Notification = Notify.Notification.new(
                summary='Frog',
                body=_('No text found. Try to grab another region.')
            )
            notification.set_icon_from_pixbuf(icon)
            notification.show()

        if copy:
            clipboard_service.set(text)

            notification: Notify.Notification = Notify.Notification.new(
                summary='Frog',
                body=_('Text extracted. You can paste it with Ctrl+V')
            )
            notification.set_icon_from_pixbuf(icon)
            notification.show()

        else:
            print(f'{text}\n')


def main(version):
    app = Application(version)
    return app.run(sys.argv)
