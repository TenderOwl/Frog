import os

import gtts
from gi.repository import GObject
from gi.repository import Gst


class TTSService(GObject.GObject):
    __gtype_name__ = 'TTSService'

    __gsignals__ = {
        'speak': (GObject.SIGNAL_RUN_LAST, None, (str,)),
        'stop': (GObject.SIGNAL_RUN_LAST, None, (bool,)),
    }

    _tld: str = "com"
    _speech_filepath: str = os.path.join(os.environ['XDG_DATA_HOME'], "speech.mp3")

    player: Gst.Element | None = None

    def __init__(self):
        super().__init__()
        Gst.init()

        self._tld = "com"

    @staticmethod
    def get_languages():
        return gtts.lang.tts_langs()

    def generate(self, text: str, lang: str = "eng") -> str | None:
        try:
            tts = gtts.gTTS(text, lang=lang)
            print("Got speech")
            tts.save(self._speech_filepath)
            print("Saved speech")

            self.emit('speak', self._speech_filepath)
            return self._speech_filepath
        except Exception as e:
            print(f"Speech error: {e}")
            return None

    def play(self, speech_file: str):
        filepath = os.path.abspath(speech_file)

        self.player = Gst.ElementFactory.make("playbin")
        self.player.set_property("uri", f"file://{filepath}")
        self.player.set_property("volume", 1.0)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_gst_message)

        self.player.set_state(Gst.State.PLAYING)

    def on_gst_message(self, _bus, message: Gst.Message):
        if message.type == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.emit('stop', True)
        elif message.type == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            print('Some error occurred while trying to play.')
            self.emit('stop', False)

    def stop_speaking(self):
        if self.player:
            self.player.set_state(Gst.State.PAUSED)


ttsservice = TTSService()
