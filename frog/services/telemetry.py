# telemetry.py
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


from typing import Any

from gi.repository import GObject
from posthog import Posthog


class TelemetryService(GObject.GObject):
    _gtype_name = 'TelemetryService'

    posthog: Posthog | None
    installation_id: str | None
    is_active: bool = True

    def __init__(self):
        super().__init__()
        self.posthog = Posthog(project_api_key='phc_HpETCN6yQKZIr8gr6mBQTd3H0SjKUBrNMI3AizoX97f',
                               host='https://eu.posthog.com')

    def set_installation_id(self, installation_id: str):
        self.installation_id = installation_id

    def set_is_active(self, is_active: bool):
        self.is_active = is_active

    def capture(self, event: str, props: Any = None):
        if self.posthog and self.is_active:
            self.posthog.capture(self.installation_id, event, props)

    def capture_page_view(self, page_name: str):
        self.posthog.capture(self.installation_id, '$pageview', {'$current_url': page_name})


telemetry = TelemetryService()
