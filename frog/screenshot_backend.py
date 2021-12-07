# screenshot_backend.py
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

import os

from typing import Optional

from pydbus import SessionBus
from gi.repository import GObject, Gio

from .config import tessdata_dir_config

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pyzbar.pyzbar import decode


class ScreenshotBackend(GObject.GObject):
    """
    ScreenshotBackend class

    This class is used to capture screenshots and recognize text from them.
    """
    def __init__(self):
        """
        Initialize ScreenshotBackend class
        """
        GObject.GObject.__init__(self)

        self.bus = SessionBus()
        self.cancelable = Gio.Cancellable.new()
        self.proxy = self.bus.get("org.gnome.Shell.Screenshot",
                                  "/org/gnome/Shell/Screenshot")

    def capture(self, lang: str) -> Optional[str]:
        """
        Captures screenshot using gnome-screenshot, extract text from it and returns it.

        If image contains QR code, it will be decoded and returned.
        Otherwise, it will be treated as image with text and processed by pytesseract and returned.
        
        If image is not recognized, returns None.

        :param lang: language to recognize text
        """
        if not self.proxy:
            return
        x, y, width, height = self.proxy.SelectArea()
        # print(f'SELECTED_AREA: {x}:{y} of {width}:{height}')

        result, filename = self.proxy.ScreenshotArea(x, y, width, height, True,
                                                     'frog-text-recognition')

        if result:
            try:
                # Try to find a QR code in the image
                data = decode(Image.open(filename))
                print(f"Image data:\n{data}")
                if len(data) > 0:
                    return data[0].data.decode('utf-8')

                # If no QR code found, try to recognize text
                text = pytesseract.image_to_string(filename,
                                                   lang=lang,
                                                   config=tessdata_dir_config)
                return text.strip()

            except Exception as e:
                print(f'Failed to decode QR code: {e}')
            finally:
                # Do some cleanup in any case
                os.remove(filename)
