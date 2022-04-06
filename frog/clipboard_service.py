from gi.repository import Gdk


class ClipboardService:
    clipboard: Gdk.Clipboard = Gdk.Display.get_default().get_clipboard()

    @classmethod
    def set(cls, value):
        cls.clipboard.set(value)


clipboard_service = ClipboardService()
