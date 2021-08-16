# window.py
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

from gettext import gettext as _

from gi.overrides.GdkPixbuf import Pixbuf
from gi.repository import Gtk, Handy, Gio, Gdk, GLib, Granite

from .config import RESOURCE_PREFIX
from .screenshot_backend import ScreenshotBackend


@Gtk.Template(resource_path='/com/github/tenderowl/frog/ui/window.ui')
class FrogWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'FrogWindow'

    toast: Granite.WidgetsToast
    main_overlay: Gtk.Overlay = Gtk.Template.Child()
    main_stack: Gtk.Stack = Gtk.Template.Child()
    lang_combo: Gtk.ComboBoxText = Gtk.Template.Child()
    shot_btn: Gtk.Button = Gtk.Template.Child()
    shot_text: Gtk.TextView = Gtk.Template.Child()
    toolbox: Gtk.Revealer = Gtk.Template.Child()
    text_clear_btn: Gtk.Button = Gtk.Template.Child()
    text_copy_btn: Gtk.Button = Gtk.Template.Child()

    # Helps to call save_window_state not more often than 500ms
    delayed_state: bool = False
    clipboard: Gtk.Clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def __init__(self, settings: Gio.Settings, **kwargs):
        Handy.init()
        super().__init__(**kwargs)

        self.settings = settings

        self.toast = Granite.WidgetsToast()
        self.main_overlay.add_overlay(self.toast)
        self.main_overlay.show_all()

        # Add Granite widget - Welcome screen.
        welcome_widget = Granite.WidgetsWelcome.new(_("Frog"), _("Grab the area to extract some text."))
        welcome_widget.set_visible(True)
        welcome_widget.show_all()
        self.main_stack.add_named(welcome_widget, 'welcome')
        self.main_stack.set_visible_child_name("welcome")

        self.set_default_icon(Pixbuf.new_from_resource_at_scale(
            f'{RESOURCE_PREFIX}/icons/com.github.tenderowl.frog.svg',
            128, 128, True
        ))

        # Setup application
        self.current_size = (450, 400)
        self.resize(*self.settings.get_value('window-size'))

        # Set default language.
        self.active_lang = "eng"
        self.lang_combo.set_active_id(self.settings.get_string("active-language"))

        # Initialize screenshot backend
        self.backend = ScreenshotBackend()

        # Connect signals
        self.shot_btn.connect('clicked', self.shot_btn_clicked)
        self.text_clear_btn.connect('clicked', self.text_clear_btn_clicked)
        self.text_copy_btn.connect('clicked', self.text_copy_btn_clicked)
        self.lang_combo.connect('changed', self.on_language_change)
        self.connect('configure-event', self.on_configure_event)
        self.connect('destroy', self.on_window_delete_event)

    def shot_btn_clicked(self, widget: Gtk.Button) -> None:
        GLib.idle_add(
            self.get_screenshot
        )

    def on_language_change(self, widget: Gtk.ComboBoxText) -> None:
        self.settings.set_string("active-language", self.lang_combo.get_active_id())

    def get_screenshot(self) -> bool:
        self.active_lang = self.lang_combo.get_active_id()

        # Just in case. Probably better add primary language in settings
        extra_lang = self.settings.get_string("extra-language")
        if self.active_lang != extra_lang:
            self.active_lang += "+" + extra_lang

        try:
            text = self.backend.capture(lang=self.active_lang)
            buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
            buffer.set_text(text)

            self.main_stack.set_visible_child_name("extracted")
            self.toolbox.set_reveal_child(True)

        except Exception as e:
            print(f"ERROR: {e}")

        return False

    def on_configure_event(self, window, event: Gdk.EventConfigure):
        if not self.delayed_state:
            GLib.timeout_add(500, self.save_window_state, window)
            self.delayed_state = True

    def save_window_state(self, user_data) -> bool:
        self.current_size = user_data.get_size()
        self.delayed_state = False
        return False

    def on_window_delete_event(self, sender: Gtk.Widget = None) -> None:
        if not self.is_maximized():
            self.settings.set_value("window-size", GLib.Variant("ai", self.current_size))
            # self.settings.set_value("window-position", GLib.Variant("ai", self.current_position))

    def text_clear_btn_clicked(self, button: Gtk.Button) -> None:
        buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
        buffer.set_text("")
        self.toolbox.set_reveal_child(False)
        self.main_stack.set_visible_child_name("welcome")

    def text_copy_btn_clicked(self, button: Gtk.Button) -> None:
        buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        self.clipboard.set_text(text, -1)

        self.toast.set_title(_("Copied!"))
        self.toast.send_notification()
