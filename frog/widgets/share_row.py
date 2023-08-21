# Copyright 2023 Andrey Maksimov
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

from gi.repository import Gtk, GLib

from frog.config import RESOURCE_PREFIX


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/share_row.ui")
class ShareRow(Gtk.ListBoxRow):
    __gtype_name__ = "ShareRow"

    box: Gtk.Box = Gtk.Template.Child()
    image: Gtk.Image = Gtk.Template.Child()
    label: Gtk.Label = Gtk.Template.Child()

    provider_name: str = 'email'

    def __init__(self, provider_name: str):
        super().__init__()

        self.provider_name = provider_name or 'email'
        self.box.set_tooltip_text(_(f"Share via {provider_name.capitalize()}"))
        self.label.set_label(provider_name.capitalize())
        self.image.set_from_icon_name(f"share-{self.provider_name.lower()}-symbolic")

    @Gtk.Template.Callback()
    def _on_released(self, *args):
        self.activate_action(
            "window.share", GLib.Variant.new_string(self.provider_name)
        )
