from gi.repository import Gdk, GObject


class ClipboardService:
    clipboard: Gdk.Clipboard = Gdk.Display.get_default().get_clipboard()

    @classmethod
    def set(cls, value: str) -> None:
        v = GObject.Value(GObject.TYPE_STRING, value)
        cls.clipboard.set_content(Gdk.ContentProvider.new_for_value(v))


clipboard_service = ClipboardService()
