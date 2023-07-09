# camera_page.py
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
from time import sleep
from typing import Any
import gi

gi.require_version('Gst', '1.0')

from gi.repository import Gtk, GObject, Gst

from frog.config import RESOURCE_PREFIX
from frog.services.camera_service import camera_service


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/camera_page.ui")
class CameraPage(Gtk.Box):
    __gtype_name__ = "CameraPage"

    __gsignals__ = {
        'go-back': (GObject.SIGNAL_RUN_LAST, None, (int,)),
    }

    overlay: Gtk.Overlay = Gtk.Template.Child()
    shot_btn: Gtk.Button = Gtk.Template.Child()
    picture: Gtk.Picture = Gtk.Template.Child()

    _stream: int
    pipeline: Gst.Pipeline

    def __init__(self):
        super().__init__()

        # initialize GStreamer
        Gst.init()

    @GObject.Property(type=int)
    def stream(self) -> int:
        return self._stream

    @stream.setter
    def stream(self, stream: int):
        self._stream = stream

    def init_stream(self, stream: int = None):
        print(f"stream: {camera_service.stream}")

        self.pipeline = Gst.Pipeline()

        source = Gst.ElementFactory.make('pipewiresrc')
        source.set_property('fd', stream)
        source.set_property('do-timestamp', True)
        source.set_property('always-copy', True)
        source.set_property('keepalive-time', 1000)

        video_queue = Gst.ElementFactory.make('queue', 'video_queue')
        videoconvert = Gst.ElementFactory.make('videoconvert')

        sink = Gst.ElementFactory.make("gtk4paintablesink", "sink")
        paintable = sink.get_property("paintable")

        # print("Creating", pipeline, pipewire_element, sink)
        #
        if not self.pipeline or not source or not sink:
            print("Not all elements could be created.")
            return

        self.pipeline.add(source)
        self.pipeline.add(video_queue)
        self.pipeline.add(videoconvert)
        self.pipeline.add(sink)

        source.link(video_queue)
        video_queue.link(videoconvert)
        videoconvert.link(sink)

        self.pipeline.set_state(Gst.State.PLAYING)

        # Set the paintable on the picture
        self.picture.set_paintable(paintable)

    @Gtk.Template.Callback()
    def _on_back_btn_clicked(self, _: Gtk.Button) -> None:
        if self.pipeline and self.pipeline.current_state != Gst.State.NULL:
            self.pipeline.set_state(Gst.State.NULL)
        self.emit('go-back', -1)
