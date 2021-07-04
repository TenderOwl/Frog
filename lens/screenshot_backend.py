from enum import Enum
from typing import Optional

from pydbus import SessionBus
from gi.repository import Gtk, GdkPixbuf, GObject, Gio

from lens.config import tessdata_dir_config

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


class CaptureType(Enum):
    AREA = 2


class ScreenshotBackend(GObject.GObject):
    def __init__(self):
        GObject.GObject.__init__(self)

        self.bus = SessionBus()
        self.cancelable = Gio.Cancellable.new()
        self.proxy = self.bus.get("org.gnome.Shell.Screenshot",
                                  "/org/gnome/Shell/Screenshot")

    def capture(self, CaptureType: CaptureType, lang: str) -> Optional[str]:
        if not self.proxy:
            return
        x, y, width, height = self.proxy.SelectArea()
        print(f'SELECT_ARED: {x}:{y} of {width}:{height}')

        result, filename = self.proxy.ScreenshotArea(x, y, width, height, True, 'image')

        if result:
            # Simple image to string
            text = pytesseract.image_to_string(filename, lang=lang, config=tessdata_dir_config)
            return text.strip()
