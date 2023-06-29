# clipboard_service.py
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

from gi.repository import Gdk, GLib
from gettext import gettext as _


class ClipboardService:
    __gtype_name__ = 'ClipboardService'

    clipboard: Gdk.Clipboard = Gdk.Display.get_default().get_clipboard()

    def set(self, value: str) -> None:
        self.clipboard.set(value)

    def _on_read_texture(self, so, res, window) -> None:
        try:
            texture = self.clipboard.read_texture_finish(res)
        except Exception as e:
            window.show_toast(
                _("No image in clipboard"))
            return
        window._paste_from_clipboard_finish(texture)
    def get_async(self, window) -> Gdk.Texture:
        self.clipboard.read_texture_async(cancellable=None, callback=self._on_read_texture, user_data=window)


clipboard_service = ClipboardService()
