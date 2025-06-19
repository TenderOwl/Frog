# language_manager.py
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

import os
import pathlib
from gettext import gettext as _
from shutil import copyfile
from typing import List, Dict
from urllib import request

from gi.repository import GObject
from loguru import logger

from frog.config import tessdata_dir, tessdata_url, tessdata_best_url
from frog.gobject_worker import GObjectWorker
from frog.types.download_state import DownloadState
from frog.types.language_item import LanguageItem


class LanguageManager(GObject.GObject):
    __gtype_name__ = 'LanguageManager'

    __gsignals__ = {
        'added': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'downloading': (GObject.SIGNAL_RUN_FIRST, None, (str, int)),
        'downloaded': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'removed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    _active_language: LanguageItem = LanguageItem(code='eng', title=_("English"))

    def __init__(self):
        super().__init__()

        self.loading_languages: Dict[str, DownloadState] = dict()

        # Cached codes of downloaded languages
        self._downloaded_codes = []
        self._need_update_cache = True

        self._languages = dict()
        self._languages["afr"] = _("Afrikaans")
        self._languages["amh"] = _("Amharic")
        self._languages["ara"] = _("Arabic")
        self._languages["asm"] = _("Assamese")
        self._languages["aze"] = _("Azerbaijani")
        self._languages["aze_cyrl"] = _("Azerbaijani - Cyrilic")
        self._languages["bel"] = _("Belarusian")
        self._languages["ben"] = _("Bengali")
        self._languages["bod"] = _("Tibetan")
        self._languages["bos"] = _("Bosnian")
        self._languages["bre"] = _("Breton")
        self._languages["bul"] = _("Bulgarian")
        self._languages["cat"] = _("Catalan; Valencian")
        self._languages["ceb"] = _("Cebuano")
        self._languages["ces"] = _("Czech")
        self._languages["chi_sim"] = _("Chinese - Simplified")
        self._languages["chi_tra"] = _("Chinese - Traditional")
        self._languages["chr"] = _("Cherokee")
        self._languages["cos"] = _("Corsican")
        self._languages["cym"] = _("Welsh")
        self._languages["dan"] = _("Danish")
        self._languages["deu"] = _("German")
        self._languages["dzo"] = _("Dzongkha")
        self._languages["ell"] = _("Greek, Modern (1453-)")
        self._languages["eng"] = _("English")
        self._languages["enm"] = _("English, Middle (1100-1500)")
        self._languages["epo"] = _("Esperanto")
        self._languages["equ"] = _("Math / equation detection module")
        self._languages["est"] = _("Estonian")
        self._languages["eus"] = _("Basque")
        self._languages["fao"] = _("Faroese")
        self._languages["fas"] = _("Persian")
        self._languages["fil"] = _("Filipino (old - Tagalog)")
        self._languages["fin"] = _("Finnish")
        self._languages["fra"] = _("French")
        self._languages["frk"] = _("German - Fraktur")
        self._languages["frm"] = _("French, Middle (ca.1400-1600)")
        self._languages["fry"] = _("Western Frisian")
        self._languages["gla"] = _("Scottish Gaelic")
        self._languages["gle"] = _("Irish")
        self._languages["glg"] = _("Galician")
        self._languages["grc"] = _("Greek, Ancient (to 1453) (contrib)")
        self._languages["guj"] = _("Gujarati")
        self._languages["hat"] = _("Haitian; Haitian Creole")
        self._languages["heb"] = _("Hebrew")
        self._languages["hin"] = _("Hindi")
        self._languages["hrv"] = _("Croatian")
        self._languages["hun"] = _("Hungarian")
        self._languages["hye"] = _("Armenian")
        self._languages["iku"] = _("Inuktitut")
        self._languages["ind"] = _("Indonesian")
        self._languages["isl"] = _("Icelandic")
        self._languages["ita"] = _("Italian")
        self._languages["ita_old"] = _("Italian - Old")
        self._languages["jav"] = _("Javanese")
        self._languages["jpn"] = _("Japanese")
        self._languages["jpn_vert"] = _("Japanese (vertical)")
        self._languages["kan"] = _("Kannada")
        self._languages["kat"] = _("Georgian")
        self._languages["kat_old"] = _("Georgian - Old")
        self._languages["kaz"] = _("Kazakh")
        self._languages["khm"] = _("Central Khmer")
        self._languages["kir"] = _("Kirghiz; Kyrgyz")
        self._languages["kmr"] = _("Kurmanji (Kurdish - Latin Script)")
        self._languages["kor"] = _("Korean")
        self._languages["kor_vert"] = _("Korean (vertical)")
        self._languages["lao"] = _("Lao")
        self._languages["lat"] = _("Latin")
        self._languages["lav"] = _("Latvian")
        self._languages["lit"] = _("Lithuanian")
        self._languages["ltz"] = _("Luxembourgish")
        self._languages["mal"] = _("Malayalam")
        self._languages["mar"] = _("Marathi")
        self._languages["mkd"] = _("Macedonian")
        self._languages["mlt"] = _("Maltese")
        self._languages["mon"] = _("Mongolian")
        self._languages["mri"] = _("Maori")
        self._languages["msa"] = _("Malay")
        self._languages["mya"] = _("Burmese")
        self._languages["nep"] = _("Nepali")
        self._languages["nld"] = _("Dutch; Flemish")
        self._languages["nor"] = _("Norwegian")
        self._languages["oci"] = _("Occitan (post 1500)")
        self._languages["ori"] = _("Oriya")
        self._languages["osd"] = _("Orientation and script detection module")
        self._languages["pan"] = _("Panjabi; Punjabi")
        self._languages["pol"] = _("Polish")
        self._languages["por"] = _("Portuguese")
        self._languages["pus"] = _("Pushto; Pashto")
        self._languages["que"] = _("Quechua")
        self._languages["ron"] = _("Romanian; Moldavian; Moldovan")
        self._languages["rus"] = _("Russian")
        self._languages["san"] = _("Sanskrit")
        self._languages["sin"] = _("Sinhala; Sinhalese")
        self._languages["slk"] = _("Slovak")
        self._languages["slv"] = _("Slovenian")
        self._languages["snd"] = _("Sindhi")
        self._languages["spa"] = _("Spanish; Castilian")
        self._languages["spa_old"] = _("Spanish; Castilian - Old")
        self._languages["sqi"] = _("Albanian")
        self._languages["srp"] = _("Serbian")
        self._languages["srp_latn"] = _("Serbian - Latin")
        self._languages["sun"] = _("Sundanese")
        self._languages["swa"] = _("Swahili")
        self._languages["swe"] = _("Swedish")
        self._languages["syr"] = _("Syriac")
        self._languages["tam"] = _("Tamil")
        self._languages["tat"] = _("Tatar")
        self._languages["tel"] = _("Telugu")
        self._languages["tgk"] = _("Tajik")
        self._languages["tha"] = _("Thai")
        self._languages["tir"] = _("Tigrinya")
        self._languages["ton"] = _("Tonga")
        self._languages["tur"] = _("Turkish")
        self._languages["uig"] = _("Uighur; Uyghur")
        self._languages["ukr"] = _("Ukrainian")
        self._languages["urd"] = _("Urdu")
        self._languages["uzb"] = _("Uzbek")
        self._languages["uzb_cyrl"] = _("Uzbek - Cyrilic")
        self._languages["vie"] = _("Vietnamese")
        self._languages["yid"] = _("Yiddish")
        self._languages["yor"] = _("Yoruba")

    @staticmethod
    def init_tessdata() -> None:
        if not os.path.exists(tessdata_dir):
            os.mkdir(tessdata_dir)

        dest_path = os.path.join(tessdata_dir, 'eng.traineddata')
        source_path = pathlib.Path('/app/share/appdata/eng.traineddata')
        if os.path.exists(dest_path):
            return

        copyfile(source_path, dest_path)

    @GObject.Property(type=GObject.TYPE_PYOBJECT)
    def active_language(self) -> LanguageItem:
        return self._active_language

    @active_language.setter
    def active_language(self, language: LanguageItem):
        logger.debug(f'Active language set to {language}')
        self._active_language = language
        self.notify('active_language')

    def get_available_codes(self):
        return [code for code in sorted(self._languages.keys(), key=lambda x: self.get_language(x))]

    def get_available_languages(self):
        return [code for code in sorted(self._languages.values())]

    def get_language(self, code: str) -> str:
        return self._languages.get(code)

    def get_language_item(self, code: str) -> LanguageItem:
        return LanguageItem(code=code, title=self.get_language(code))

    def get_language_code(self, language: str) -> str:
        for code, lang in self._languages.items():
            if lang == language:
                return code

    def get_downloaded_codes(self, force: bool = False) -> List[str]:
        if self._need_update_cache or force:
            self._downloaded_codes = [os.path.splitext(lang_file)[0]
                                      for lang_file in os.listdir(tessdata_dir)]
            self._need_update_cache = False
            logger.debug(f"Cache downloaded codes: {self._downloaded_codes}")

        recognized_codes = []
        for code in self._downloaded_codes:
            if code not in self._languages:
                logger.warning(f'Unrecognized language code: {code}')
                continue
            recognized_codes.append(code)

        return sorted(recognized_codes, key=lambda x: self.get_language(x))

    def get_downloaded_languages(self, force: bool = False) -> List[str]:
        return sorted({self.get_language(code) for code in self.get_downloaded_codes(force)})

    def download(self, code):
        self.emit('added', code)
        self.loading_languages[code] = DownloadState()
        self.emit('downloading', code, 0.1)
        GObjectWorker.call(self.download_begin, (code,), self.download_done)

    def download_begin(self, code):

        def update_progress(block_num, block_size, total_size):
            progress = int(block_num * block_size * 100 / total_size)
            self.emit('downloading', code, progress)

        tessfile = f'{code}.traineddata'
        tessfile_path = os.path.join(tessdata_dir, tessfile)
        logger.debug(f'Data will be extracted to: {tessfile_path}')
        try:
            request.urlretrieve(tessdata_best_url + tessfile, tessfile_path, update_progress)
            return code
        except Exception as e:
            logger.debug(e)
            try:
                logger.debug(f"{code} not found in tessdata_best, checking tessdata")
                request.urlretrieve(tessdata_url + tessfile, tessfile_path)
                return code
            except Exception as e2:
                logger.debug(e2)
                logger.debug(f"{code} was not found at tessdata")

    def download_done(self, code):
        self._need_update_cache = True
        if code:
            self.loading_languages.pop(code)
        self.emit('downloaded', code)

    def remove_language(self, code):
        os.remove(os.path.join(tessdata_dir, f"{code}.traineddata"))
        self._need_update_cache = True
        self.emit('removed', code)


language_manager = LanguageManager()
