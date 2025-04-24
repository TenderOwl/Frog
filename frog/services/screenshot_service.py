# screenshot_service.py
#
# Copyright 2022-2025 Andrey Maksimov
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
from gettext import gettext as _

from gi.repository import GObject, Gio, GLib, Xdp
from loguru import logger

from frog.config import tessdata_config
from frog.services.telemetry import telemetry

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pyzbar.pyzbar import decode


class ScreenshotService(GObject.GObject):
    """
    ScreenshotBackend class

    This class is used to capture screenshots and recognize text from them.
    """

    __gtype_name__ = "ScreenshotService"

    __gsignals__ = {
        "error": (GObject.SIGNAL_RUN_LAST, None, (str,)),
        "decoded": (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (
                str,
                bool,
            ),
        ),
    }

    def __init__(self):
        """
        Initialize ScreenshotBackend class
        """
        GObject.GObject.__init__(self)

        self.cancelable: Gio.Cancellable = Gio.Cancellable.new()
        self.cancelable.connect(self.capture_cancelled)
        self.portal = Xdp.Portal()

    def capture(self, lang: str, copy: bool = False) -> None:
        """
        Captures screenshot using gnome-screenshot, extract text from it and returns it.

        If image contains QR code, it will be decoded and returned.
        Otherwise, it will be treated as image with text and processed
        by pytesseract and returned.

        If image is not recognized, returns None.
        """
        telemetry.capture('screenshot capture', {'language': lang})
        self.portal.take_screenshot(
            None,
            Xdp.ScreenshotFlags.INTERACTIVE,
            self.cancelable,
            self.take_screenshot_finish,
            [lang, copy],
        )

    def take_screenshot_finish(self, source_object, res: Gio.Task, user_data):
        if res.had_error():
            return self.emit("error", _("Can't take a screenshot."))

        lang, copy = user_data

        filename = self.portal.take_screenshot_finish(res)
        # Remove file:// from the path
        filename = filename[7:]
        filename = GLib.Uri.unescape_string(filename)
        self.decode_image(lang, filename, copy, True)

    def decode_image(self,
                     lang: str,
                     file: str | Image.Image,
                     copy: bool = False,
                     remove_source: bool = False,
                     ) -> None:
        # Check if `file` is a filepath and mark it for deletion
        if not isinstance(file, str) or not os.path.exists(file):
            remove_source = False
            logger.debug('Remove source set to False')

        logger.debug(f"Decoding with {lang} language.")
        extracted = None
        try:
            # Try to find a QR code in the image
            data = decode(Image.open(file))
            if len(data) > 0:
                extracted = data[0].data.decode("utf-8")

            # If no QR code found, try to recognize text
            else:
                # We cannot pass the same image object from above, since
                # pyzbar.decode runs Image.load() internally, as does
                # pytesseract.image_to_string(). However, a second load() will
                # close the file leading to seek errors on NoneType:
                # > If the file associated with the image was opened by Pillow,
                # > then this method will close it.
                # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.load
                text = pytesseract.image_to_string(
                    Image.open(file), lang=lang, config=tessdata_config
                )
                extracted = text.strip()

        except Exception as e:
            logger.debug("ERROR: ", e)
            self.emit("error", "Failed to decode data.")

        finally:
            if remove_source:
                try:
                    logger.debug(f"Removing {file}")
                    os.unlink(file)
                except Exception as e:
                        logger.debug(f"Error deleting {file}: {e}")

        if extracted:
            logger.debug("Extracted successfully")
            self.emit("decoded", extracted, copy)

        else:
            self.emit("error", "No text found.")

    def capture_cancelled(self, cancellable: Gio.Cancellable) -> None:
        telemetry.capture('screenshot cancelled')
        self.emit("error", "Cancelled")
