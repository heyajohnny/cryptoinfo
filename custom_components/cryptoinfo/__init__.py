from custom_components.cryptoinfo.config_flow import CryptoInfoData
from .const.const import _LOGGER, DOMAIN

from homeassistant.const import Platform

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    """Set up the CryptoInfo platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = CryptoInfoData()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("__init__ set up")
    return True
