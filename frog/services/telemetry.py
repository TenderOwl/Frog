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


telemetry = TelemetryService()
