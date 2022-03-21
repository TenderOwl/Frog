# about_dialog.py
#
# MIT License
#
# Copyright (c) 2021 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import datetime
from gettext import gettext as _

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, version, transient_for, modal=False):
        super().__init__(transient_for=transient_for, modal=modal)
        self.set_program_name("Frog")
        self.set_comments(_('Frog can help you to instantly extract text\nfrom any QR code, image, video, PDF, etc.'))
        self.set_copyright(f'© {datetime.date.today().year}, Tender Owl')
        self.set_website("https://getfrog.app")
        self.set_website_label(_('Learn more about Frog'))
        self.set_license_type(Gtk.License.MIT_X11)
        self.set_version(version)

        self.connect('response', self.on_close)

    def on_close(self, sender: Gtk.Widget, response_id: int) -> None:
        self.destroy()
