from gi.repository import Gtk

from frog.language_dialog import LanguageItem


class ListMenuRow(Gtk.Label):
    def __init__(self, item: LanguageItem):
        super(ListMenuRow, self).__init__()

        self.item = item
        self.set_label(item.title)
        self.set_halign(Gtk.Align.START)
