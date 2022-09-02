from gi.repository import Gtk, Adw, GLib

from frog.config import RESOURCE_PREFIX
from frog.language_manager import language_manager


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/language_row.ui')
class LanguageRow(Gtk.Overlay):
    __gtype_name__ = 'LanguageRow'

    label: Gtk.Label = Gtk.Template.Child()
    download_widget: Gtk.Button = Gtk.Template.Child()
    progress_bar: Gtk.ProgressBar = Gtk.Template.Child()
    revealer: Gtk.Revealer = Gtk.Template.Child()

    def __init__(self, lang_code, lang_title, **kwargs):
        super().__init__(**kwargs)

        self.lang_code = lang_code
        self.lang_title = lang_title

        self.download_widget.connect('clicked', self.download_clicked)
        language_manager.connect('downloading', self.update_progress)
        language_manager.connect('downloaded', self.on_downloaded)

        self.label.set_label(self.lang_title)
        self.progress_bar.set_fraction(0.14)

        GLib.idle_add(self.update_ui)

    def update_ui(self):
        # Downloaded
        if self.lang_code in language_manager.get_downloaded_codes():
            self.download_widget.set_icon_name('user-trash-symbolic')
            self.download_widget.set_sensitive(True)
            self.get_style_context().add_class("downloaded")
            self.download_widget.get_style_context().add_class("destructive-action")
        # In progress
        elif self.lang_code in language_manager.loading_languages:
            self.download_widget.set_sensitive(False)
            self.get_style_context().remove_class("downloaded")
        # Not yet
        else:
            self.get_style_context().remove_class("downloaded")
            self.download_widget.set_sensitive(True)
            self.download_widget.get_style_context().remove_class("destructive-action")
            self.download_widget.set_icon_name('folder-download-symbolic')
            self.revealer.set_reveal_child(False)

    def update_progress(self, event, code: str, progress: float) -> None:
        GLib.idle_add(self.late_update, code, progress)

    def late_update(self, code, progress):
        if self.lang_code == code:
            if not self.revealer.get_reveal_child():
                self.revealer.set_reveal_child(True)

            self.progress_bar.set_fraction(progress / 100)
            self.progress_bar.set_pulse_step(0.05)
            print(f'Downloading {progress / 100}')

            if progress == 100:
                self.revealer.set_reveal_child(False)

    def download_clicked(self, widget: Gtk.Button) -> None:
        if self.lang_code in language_manager.loading_languages:
            return

        if self.lang_code in language_manager.get_downloaded_codes():
            language_manager.remove_language(self.lang_code)
            self.update_ui()
            return

        language_manager.download(self.lang_code)
        self.update_ui()

    def on_downloaded(self, sender, code):
        if self.lang_code == code:
            GLib.idle_add(self.update_ui)
