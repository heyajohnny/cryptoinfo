from .config_flow import CryptoInfoData
from .const.const import _LOGGER, DOMAIN

from homeassistant.const import Platform

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry) -> bool:
    """Set up the CryptoInfo platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = CryptoInfoData(hass)
        await hass.data[DOMAIN].async_initialize()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("__init__ set up")
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Unload a config entry."""
    # Save data before unloading
    if DOMAIN in hass.data:
        await hass.data[DOMAIN].store.async_save()

    # Unload the sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    return unload_ok
