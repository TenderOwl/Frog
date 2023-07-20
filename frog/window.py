# window.py
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
from io import BytesIO
from mimetypes import guess_type
from typing import List
from urllib.parse import urlparse

from gi.repository import Gtk, Adw, Gio, GLib, Gdk, GObject

from frog.gobject_worker import GObjectWorker
from frog.language_manager import language_manager
from frog.services.camera_service import camera_service
from frog.services.clipboard_service import clipboard_service
from frog.services.screenshot_service import ScreenshotService
from frog.widgets.camera_page import CameraPage
from frog.widgets.extracted_page import ExtractedPage
from frog.widgets.list_menu_row import ListMenuRow
from frog.widgets.preferences_dialog import PreferencesDialog
from frog.widgets.welcome_page import WelcomePage


@Gtk.Template(resource_path="/com/github/tenderowl/frog/ui/window.ui")
class FrogWindow(Adw.ApplicationWindow):
    __gtype_name__ = "FrogWindow"

    gtk_settings: Gtk.Settings = Gtk.Settings.get_default()

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()

    main_leaflet: Adw.Leaflet = Gtk.Template.Child()
    welcome_page: WelcomePage = Gtk.Template.Child()
    camera_page: CameraPage = Gtk.Template.Child()
    extracted_page: ExtractedPage = Gtk.Template.Child()

    # Helps to call save_window_state not more often than 500ms
    delayed_state: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_size = None
        self.open_file_dlg = None
        self.settings = Gtk.Application.get_default().props.settings

        # self.infobar = Gtk.InfoBar(visible=True, revealed=False)
        # self.infobar.set_show_close_button(True)
        # self.infobar.connect('response', self.on_infobar_response)
        #
        # self.infobar_label = Gtk.Label()
        # self.infobar.add_child(self.infobar_label)
        #
        # self.main_leaflet.append(self.infobar)  # , False, True, 2)

        # Init drag-n-drop controller
        drop_target_main: Gtk.DropTarget = Gtk.DropTarget.new(
            type=Gdk.FileList, actions=Gdk.DragAction.COPY
        )
        drop_target_main.connect("drop", self.on_dnd_drop)
        drop_target_main.connect("enter", self.on_dnd_enter)
        drop_target_main.connect("leave", self.on_dnd_leave)
        self.main_leaflet.add_controller(drop_target_main)

        # drop_target_textview: Gtk.DropTarget = Gtk.DropTarget.new(
        #     type=Gdk.FileList, actions=Gdk.DragAction.COPY
        # )
        # drop_target_textview.connect("drop", self.on_dnd_drop)
        # drop_target_textview.connect("enter", self.on_dnd_enter)
        # drop_target_textview.connect("leave", self.on_dnd_leave)
        # self.shot_text.add_controller(drop_target_textview)

        # Setup application
        self.props.default_width = self.settings.get_int("window-width")
        self.props.default_height = self.settings.get_int("window-height")

        # Initialize screenshot backend
        self.backend = ScreenshotService()
        self.backend.connect("decoded", self.on_shot_done)
        self.backend.connect("error", self.on_shot_error)

        self.camera_page.connect('go-back', self.show_welcome_page)
        self.camera_page.connect('image-grabbed', self._on_cam_image_grabbed)
        self.extracted_page.connect('go-back', self.show_welcome_page)

        clipboard_service.connect('paste_from_clipboard', self._on_paste_from_clipboard)
        clipboard_service.connect('error', self.display_error)

        camera_service.connect('camera_stream', self._on_camera_stream)

        # # self.text_copy_btn.connect('clicked', self.text_copy_btn_clicked)
        # self.languages_list.connect("row-activated", self.on_language_change)
        # self.connect("notify::default-width", self.on_configure_event)
        # self.connect("notify::default-height", self.on_configure_event)
        # self.connect("destroy", self.on_window_delete_event)

    @GObject.Property(type=str)
    def active_lang(self):
        return self.settings.get_string("active-language")

    @active_lang.setter
    def active_lang(self, lang_code: str):
        self.settings.set_string("active-language", lang_code)

    def on_language_change(self, widget: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        child: ListMenuRow = row.get_child()
        active_id = child.item.code if child.item else None

        if active_id and active_id != "-1":
            self.settings.set_string("active-language", active_id)
            self.text_shot_btn.set_sensitive(True)
            self.lang_combo.set_label(child.item.title)
            widget.get_parent().get_parent().hide()
        else:
            self.text_shot_btn.set_sensitive(False)

    def get_screenshot(self, copy: bool = False) -> None:
        lang = self.get_language()
        # self.welcome_page.spinner.start()
        self.hide()
        self.backend.capture(lang, copy)

    def get_language(self) -> str:
        self.active_lang = language_manager.active_language.code
        # Just in case. Probably better add primary language in settings
        extra_lang = self.settings.get_string("extra-language")
        # if self.active_lang != extra_lang:
        #     self.active_lang = f'{self.active_lang}+{extra_lang}'

        return f"{self.active_lang}+{extra_lang}"

    def on_shot_done(self, sender, text: str, copy: bool) -> None:
        is_url = self.uri_validator(text)
        try:
            self.extracted_page.extracted_text = text

            if self.settings.get_boolean("autocopy") or copy:
                clipboard_service.set(text)
                self.show_toast(_("Text copied to clipboard"))

            # If text is a URL we could show user Toast with suggestion to open it
            # Or automatically open it, if this setting is set.
            if is_url:
                if self.settings.get_boolean("autolinks"):
                    Gtk.show_uri(None, text, Gdk.CURRENT_TIME)
                    self.show_toast(
                        _("QR-code URL opened"),
                        priority=Adw.ToastPriority.HIGH
                    )
                else:
                    toast = Adw.Toast(
                        title=_("QR-code contains URL."),
                        button_label=_("Open"),
                        priority=Adw.ToastPriority.HIGH,
                    )
                    toast.set_detailed_action_name(f'app.show_uri("{text}")')
                    self.toast_overlay.add_toast(toast)

            self.main_leaflet.set_visible_child_name("extracted")

        except Exception as e:
            print(f"ERROR: {e}")

        finally:
            self.present()
            self.welcome_page.spinner.stop()

    def on_shot_error(self, _sender, message: str) -> None:
        self.present()
        self.welcome_page.spinner.stop()
        print("on_shot_error?", message)
        if message:
            self.show_toast(message)

    def grab_camera(self):
        camera_service.grab_camera()

    def _on_camera_stream(self, _sender, stream: int):
        self.main_leaflet.set_visible_child_name('camera')
        self.camera_page.init_stream(stream)

    def _on_cam_image_grabbed(self, _sender, image_path: str):
        try:
            self.welcome_page.spinner.start()
            GObjectWorker.call(self.backend.decode_image, (self.get_language(), image_path))
        except GLib.Error as e:
            if not e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                print(e)

    def open_image(self):
        self.open_file_dlg: Gtk.FileDialog = Gtk.FileDialog()

        file_filters: Gio.ListStore = Gio.ListStore.new(Gtk.FileFilter)
        file_filter = Gtk.FileFilter()
        file_filter.set_name(_("Supported image files"))
        file_filter.add_mime_type("image/png")
        file_filter.add_mime_type("image/jpeg")
        file_filter.add_mime_type("image/jpg")
        file_filters.append(file_filter)

        self.open_file_dlg.set_title(_("Open image to extract text"))
        self.open_file_dlg.set_filters(file_filters)

        self.open_file_dlg.open(self, None, self.on_open_image)

    def on_open_image(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            item = dialog.open_finish(result)
            lang = self.get_language()
            self.welcome_page.spinner.start()
            GObjectWorker.call(self.backend.decode_image, (lang, item.get_path()))
        except GLib.Error as e:
            if not e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                print(e)

    def _on_paste_from_clipboard(self, _sender: GObject,
                                 texture: Gdk.Texture):
        pngbytes = BytesIO(texture.save_to_png_bytes().get_data())
        try:
            lang = self.get_language()
            self.welcome_page.spinner.start()
            GObjectWorker.call(self.backend.decode_image, (lang, pngbytes))
        except GLib.Error as e:
            if not e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                print(e)

    def on_paste_from_clipboard(self, sender) -> None:
        clipboard_service.read_texture()

    def display_error(self, sender, error) -> None:
        print(f"Error happened: {error}")
        message = (str(error).split(":")[-1]) if not isinstance(error, str) else error
        self.show_toast(message)

    def on_dnd_enter(self, drop_target, x, y):
        print("DND Enter", drop_target)
        self.add_css_class("drop_hover")
        return Gdk.DragAction.COPY

    def on_dnd_leave(self, user_data=None):
        print("DND Leave")
        self.remove_css_class("drop_hover")

    def on_dnd_drop(self, drop_target,
                    value: Gdk.FileList,
                    x: int, y: int
                    ) -> None:
        files: List[Gio.File] = value.get_files()
        if not files:
            return

        item = files[0]
        (mimetype, encoding) = guess_type(item.get_path())
        print(f"Dropped item ({mimetype}): {item.get_path()}")
        if not mimetype or not mimetype.startswith("image"):
            return self.show_toast(_("Only images can be processed that way."))

        lang = self.get_language()
        self.welcome_page.spinner.start()
        GObjectWorker.call(self.backend.decode_image, (lang, item.get_path()))

    def on_configure_event(self, window, event):
        if not self.delayed_state:
            GLib.timeout_add(500, self.save_window_state, window)
            self.delayed_state = True

    def on_infobar_response(
            self, infobar: Gtk.InfoBar, response_type: Gtk.ResponseType
    ):
        if response_type == Gtk.ResponseType.CLOSE:
            self.infobar.set_revealed(False)

    def save_window_state(self, window: Gtk.Window) -> bool:
        self.current_size = window.get_default_size()
        self.settings.set_int("window-width", self.current_size[0])
        self.settings.set_int("window-height", self.current_size[1])
        self.settings.sync()
        self.delayed_state = False
        return False

    def on_window_delete_event(self, sender: Gtk.Widget = None) -> None:
        if not self.is_maximized():
            self.settings.set_int("window-width", self.current_size[0])
            self.settings.set_int("window-height", self.current_size[1])

    def on_copy_to_clipboard(self, sender) -> None:
        text = self.extracted_page.extracted_text
        clipboard_service.set(text)
        self.show_toast(_("Text copied"))

    def show_preferences(self):
        # dialog = LanguagePacksDialog(self)
        dialog = PreferencesDialog(settings=self.settings, parent=self)
        dialog.present()

    def show_welcome_page(self, *_):
        self.main_leaflet.set_visible_child_name('welcome')

    def show_toast(self, title: str, timeout: int = 2,
                   priority: Adw.ToastPriority = Adw.ToastPriority.NORMAL):
        self.toast_overlay.add_toast(
            Adw.Toast(title=title, timeout=timeout, priority=priority)
        )

    def uri_validator(self, link) -> bool:
        try:
            result = urlparse(link)
            return all([result.scheme, result.netloc])
        except Exception as e:
            print(e)
            return False
