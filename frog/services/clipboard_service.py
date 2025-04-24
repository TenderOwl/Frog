# clipboard_service.py
#
# Copyright 2021-2025 Andrey Maksimov
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

from gi.repository import Gdk, GObject, Gio
from loguru import logger

from frog.services.telemetry import telemetry


class ClipboardService(GObject.GObject):
    __gtype_name__ = 'ClipboardService'

    __gsignals__ = {
        'paste_from_clipboard': (GObject.SIGNAL_RUN_FIRST, None, (Gdk.Texture,)),
        'error': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    clipboard: Gdk.Clipboard = Gdk.Display.get_default().get_clipboard()

    def __init__(self):
        super().__init__()

    def set(self, value: str) -> None:
        self.clipboard.set(value)
        telemetry.capture('clipboard set')

    def _on_read_texture(self, _sender: GObject.GObject, result: Gio.AsyncResult) -> None:
        try:
            texture = self.clipboard.read_texture_finish(result)
        except Exception as e:
            logger.debug(e)
            return self.emit('error', _("No image in clipboard"))
        self.emit('paste_from_clipboard', texture)

    def read_texture(self) -> None:
        telemetry.capture('clipboard read texture')
        self.clipboard.read_texture_async(cancellable=None,
                                          callback=self._on_read_texture)


clipboard_service = ClipboardService()
