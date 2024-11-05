from .storage_helper import CryptoInfoStore


class CryptoInfoData:
    def __init__(self, hass):
        self._hass = hass
        self.store = CryptoInfoStore(hass)
        self._min_time_between_requests = 1.0

    async def async_initialize(self):
        """Initialize the data from storage."""
        await self.store.async_load()
        self._min_time_between_requests = self.store.data.get(
            "min_time_between_requests", 1.0
        )

    @property
    def min_time_between_requests(self):
        return self._min_time_between_requests

    @min_time_between_requests.setter
    def min_time_between_requests(self, value):
        self._min_time_between_requests = value
        self.store.data["min_time_between_requests"] = value
        self._hass.async_create_task(self.store.async_save())
