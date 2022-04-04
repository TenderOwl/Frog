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
from gi.repository import Gtk, Adw, Gio, Gdk, GLib, GObject

from .config import RESOURCE_PREFIX
from .gobject_worker import GObjectWorker
from .language_dialog import LanguagePacksDialog
from .language_manager import language_manager
from .screenshot_backend import ScreenshotBackend


@Gtk.Template(resource_path='/com/github/tenderowl/frog/ui/window.ui')
class FrogWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FrogWindow'

    gtk_settings: Gtk.Settings = Gtk.Settings.get_default()

    spinner: Gtk.Spinner = Gtk.Template.Child()
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    main_box: Gtk.Box = Gtk.Template.Child()
    main_stack: Adw.ViewStack = Gtk.Template.Child()
    text_scrollview: Gtk.ScrolledWindow = Gtk.Template.Child()
    lang_combo: Gtk.ComboBoxText = Gtk.Template.Child()
    toolbox: Gtk.Revealer = Gtk.Template.Child()
    text_shot_btn: Gtk.Button = Gtk.Template.Child()
    text_clear_btn: Gtk.Button = Gtk.Template.Child()
    text_copy_btn: Gtk.Button = Gtk.Template.Child()

    # Helps to call save_window_state not more often than 500ms
    delayed_state: bool = False
    clipboard: Gdk.Clipboard

    def __init__(self, settings: Gio.Settings, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings
        self.clipboard = self.get_clipboard()

        self.infobar = Gtk.InfoBar(visible=True, revealed=False)
        self.infobar.set_show_close_button(True)
        self.infobar.connect('response', self.on_infobar_response)

        self.infobar_label = Gtk.Label()
        self.infobar.add_child(self.infobar_label)

        self.main_box.append(self.infobar)  # , False, True, 2)

        self.shot_text = Gtk.TextView()
        self.shot_text.set_editable(False)
        self.shot_text.set_visible(True)
        self.shot_text.set_left_margin(8)
        self.shot_text.set_right_margin(8)
        self.shot_text.set_top_margin(8)
        self.shot_text.set_bottom_margin(8)

        self.text_scrollview.set_child(self.shot_text)

        self.text_shot_btn.set_tooltip_markup(f'{_("Take a shot")}\n<small>&lt;Control&gt;g</small>')

        self.main_stack.set_visible_child_name("welcome")

        # self.set_default_icon(Pixbuf.new_from_resource_at_scale(
        #     f'{RESOURCE_PREFIX}/icons/com.github.tenderowl.frog.svg',
        #     128, 128, True
        # ))

        # Setup application
        self.current_size = (450, 400)
        saved_width, saved_height = self.settings.get_value('window-size')
        self.props.default_width = saved_width
        self.props.default_height = saved_height

        # Set default language.
        language_manager.connect('downloading', self.on_language_downloading)
        language_manager.connect('downloaded', self.on_language_downloaded)
        language_manager.connect('removed', self.on_language_removed)
        self.fill_lang_combo()
        if not language_manager.get_downloaded_codes():
            self.text_shot_btn.set_sensitive(False)

        # Initialize screenshot backend
        self.backend = ScreenshotBackend()
        self.backend.connect('decoded', self.on_shot_done)
        self.backend.connect('error', self.on_shot_error)

        # Connect signals
        self.text_shot_btn.connect('clicked', self.on_take_shot_clicked)
        self.text_clear_btn.connect('clicked', self.text_clear_btn_clicked)
        self.text_copy_btn.connect('clicked', self.text_copy_btn_clicked)
        self.lang_combo.connect('changed', self.on_language_change)
        self.connect('notify::default-width', self.on_configure_event)
        self.connect('notify::default-height', self.on_configure_event)
        self.connect('destroy', self.on_window_delete_event)

    @property
    def active_lang(self):
        return self.settings.get_string("active-language")

    @active_lang.setter
    def active_lang(self, lang_code: str):
        self.settings.set_string("active-language", lang_code)

    @Gtk.Template.Callback()
    def on_take_shot_clicked(self, button: Gtk.Button):
        self.get_screenshot()

    @Gtk.Template.Callback()
    def on_configure_language_clicked(self, button: Gtk.Button):
        self.lang_prefs_btn_clicked()

    def fill_lang_combo(self):
        self.lang_combo.remove_all()

        downloaded_languages = language_manager.get_downloaded_languages(force=True)
        for lang in downloaded_languages:
            self.lang_combo.append(language_manager.get_language_code(lang), lang)

        self.lang_combo.set_active(0)

        if self.active_lang:
            self.lang_combo.set_active_id(self.active_lang.rsplit('+')[0])

        if not downloaded_languages:
            self.lang_combo.append("-1", _("No languages"))
            self.lang_combo.set_active_id("-1")

    def on_language_change(self, widget: Gtk.ComboBoxText) -> None:
        active_id = self.lang_combo.get_active_id()
        if active_id and active_id != "-1":
            self.settings.set_string("active-language", active_id)
            self.text_shot_btn.set_sensitive(True)
        else:
            self.text_shot_btn.set_sensitive(False)

    def get_screenshot(self, copy: bool = False) -> None:
        self.active_lang = self.lang_combo.get_active_id()

        self.hide()

        # Just in case. Probably better add primary language in settings
        extra_lang = self.settings.get_string("extra-language")
        if self.active_lang != extra_lang:
            self.active_lang = f'{self.active_lang}+{extra_lang}'

        self.backend.capture(self.active_lang, copy)

    def on_shot_done(self, sender, text: str, copy: bool) -> None:
        try:
            # text = self.backend.capture(lang=self.active_lang)
            buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
            buffer.set_text(text)

            if copy:
                self.copy_to_clipboard(text)

            self.main_stack.set_visible_child_name("extracted")
            self.toolbox.set_reveal_child(True)

        except Exception as e:
            print(f"ERROR: {e}")

        self.show()

    def on_shot_error(self, sender, message: str) -> None:
        print(f"ERROR: '{message}'")
        if message:
            self.on_screenshot_error(self, 'Whoops')
        self.show()

    def on_screenshot_error(self, sender, error) -> None:
        if not isinstance(error, str):
            self.infobar_label.set_text(str(error).split(':')[-1])
        else:
            self.infobar_label.set_text(error)
        self.infobar.set_revealed(True)
        self.infobar.set_visible(True)
        self.infobar.set_message_type(Gtk.MessageType.ERROR)

    def on_configure_event(self, window, event):
        if not self.delayed_state:
            GLib.timeout_add(500, self.save_window_state, window)
            self.delayed_state = True

    def on_infobar_response(self, infobar: Gtk.InfoBar, response_type: Gtk.ResponseType):
        if response_type == Gtk.ResponseType.CLOSE:
            self.infobar.set_revealed(False)

    def save_window_state(self, window: Gtk.Window) -> bool:
        self.current_size = window.get_default_size()
        self.delayed_state = False
        return False

    def on_window_delete_event(self, sender: Gtk.Widget = None) -> None:
        if not self.is_maximized():
            self.settings.set_value("window-size", GLib.Variant("ai", self.current_size))
            self.settings.set_value("window-position", GLib.Variant("ai", self.current_position))

    def text_clear_btn_clicked(self, button: Gtk.Button) -> None:
        buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
        buffer.set_text("")
        self.toolbox.set_reveal_child(False)
        self.main_stack.set_visible_child_name("welcome")

    def text_copy_btn_clicked(self, button: Gtk.Widget) -> None:
        buffer: Gtk.TextBuffer = self.shot_text.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        self.copy_to_clipboard(text)

    def copy_to_clipboard(self, text):
        self.clipboard.set(text)
        self.show_toast(_("Copied!"))

    def lang_prefs_btn_clicked(self) -> None:
        dialog = LanguagePacksDialog(self)
        dialog.show()

    def on_language_downloading(self, sender, lang_code: str):
        print(f'on_language_downloading: {lang_code}')

    def on_language_downloaded(self, sender, lang_code: str):
        language = language_manager.get_language(lang_code)
        print('on_language_downloaded: ' + language)
        self.show_toast(_(f'{language} language downloaded.'))
        self.fill_lang_combo()

    def on_language_removed(self, sender, lang_code: str):
        print('on_language_removed: ' + lang_code)
        self.fill_lang_combo()

    def show_toast(self, title, timeout: int = 2) -> None:
        self.toast_overlay.add_toast(Adw.Toast(title=title, timeout=timeout))
