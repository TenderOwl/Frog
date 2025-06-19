# config.py
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

APP_ID = "com.github.tenderowl.frog"
RESOURCE_PREFIX = "/com/github/tenderowl/frog"

# This is based from the XDG Base Directory specification.
if not os.getenv('XDG_DATA_HOME'):
    os.environ['XDG_DATA_HOME'] = os.path.expanduser('~/.local/share')

if not os.path.exists(os.path.join(os.environ['XDG_DATA_HOME'], 'tessdata')):
    os.mkdir(os.path.join(os.environ['XDG_DATA_HOME'], 'tessdata'))

tessdata_url = "https://github.com/tesseract-ocr/tessdata/raw/main/"
tessdata_best_url = "https://github.com/tesseract-ocr/tessdata_best/raw/main/"
tessdata_dir = os.path.join(os.environ['XDG_DATA_HOME'], 'tessdata')
tessdata_config = f'--tessdata-dir {tessdata_dir} --oem 1'
