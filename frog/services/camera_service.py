from gettext import gettext as _
from gi.repository import GObject, Gio
from gi.repository import Xdp


class CameraService(GObject.GObject):
    __gtype_name__ = 'CameraService'

    __gsignals__ = {
        'camera_stream': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'error': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    portal: Xdp.Portal

    stream: int = GObject.Property(type=int)

    def __init__(self):
        super().__init__()

        self.portal = Xdp.Portal()

    @GObject.Property(type=bool, default=False)
    def is_camera_present(self):
        return self.portal.is_camera_present

    def grab_camera(self):
        self.portal.access_camera(
            parent=None,
            flags=Xdp.CameraFlags.NONE,
            cancellable=None,
            callback=self._on_access_camera)

    def _on_access_camera(self, portal: Xdp.Portal,
                          result: Gio.AsyncResult):
        is_granted = self.portal.access_camera_finish(result)
        if not is_granted:
            print('Camera access restricted')
            self.emit('error', _('Access denied'))
            return
        self.stream = self.portal.open_pipewire_remote_for_camera()
        self.emit('camera_stream', self.stream)


camera_service = CameraService()
