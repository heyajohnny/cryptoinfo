#!/usr/bin/env python3
"""
Config flow component for Cryptoinfo
Author: Johnny Visser
"""

from typing import Any
from collections.abc import Mapping

from homeassistant.helpers.selector import selector
from homeassistant.helpers import config_validation as cv
from homeassistant import config_entries

from .const.const import (
    _LOGGER,
    DOMAIN,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_MULTIPLIER,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    CONF_ID,
)

import voluptuous as vol

PLACEHOLDERS = {
    "description_help": "For more information, see the <a href='https://github.com/heyajohnny/cryptoinfo' target='_blank'>documentation</a>.",
    "id_help": "Unique name for the sensor",
    "currency_name_help": "One of the currency names in <a href='https://api.coingecko.com/api/v3/simple/supported_vs_currencies' target='_blank'>this list</a>.",
    "cryptocurrency_name_help": "The 'id' value from one of the coins/tokens in <a href='https://api.coingecko.com/api/v3/coins/list' target='_blank'>this list</a>.",
    "unit_of_measurement_help": "Do you want to use a currency symbol? (<a href='https://en.wikipedia.org/wiki/Currency_symbol#List_of_currency_symbols_currently_in_use' target='_blank'>Symbol list</a>)",
    "multiplier_help": "The number of coins/tokens",
    "update_frequency_help": "How often should the value be refreshed? Beware of the <a href='https://support.coingecko.com/hc/en-us/articles/4538771776153-What-is-the-rate-limit-for-CoinGecko-API-public-plan' target='_blank'>CoinGecko rate limit</a> when tracking multiple cryptocurrencies.",
}


class CryptoInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_reconfigure(self, user_input: Mapping[str, Any] | None = None):
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry
        if user_input:
            return self.async_update_reload_and_abort(
                entry, data=user_input, reason="reconfigure_successful"
            )

        return await self._redo_configuration(entry.data)

    async def _redo_configuration(self, entry_data: Mapping[str, Any]):
        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(CONF_ID, default=entry_data[CONF_ID]): str,
                vol.Required(
                    CONF_CRYPTOCURRENCY_NAME,
                    default=entry_data[CONF_CRYPTOCURRENCY_NAME],
                ): str,
                vol.Required(
                    CONF_CURRENCY_NAME, default=entry_data[CONF_CURRENCY_NAME]
                ): str,
                vol.Optional(
                    CONF_UNIT_OF_MEASUREMENT,
                    default=entry_data[CONF_UNIT_OF_MEASUREMENT],
                ): str,
                vol.Required(
                    CONF_MULTIPLIER, default=entry_data[CONF_MULTIPLIER]
                ): cv.positive_int,
                vol.Required(
                    CONF_UPDATE_FREQUENCY, default=entry_data[CONF_UPDATE_FREQUENCY]
                ): cv.positive_float,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=cryptoinfo_schema,
            description_placeholders=PLACEHOLDERS,
        )

    async def async_step_user(self, info):
        if info is not None:
            await self.async_set_unique_id(info["id"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Cryptoinfo for " + info["id"], data=info
            )

        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(CONF_ID, default=""): str,
                vol.Required(CONF_CRYPTOCURRENCY_NAME, default="bitcoin"): str,
                vol.Required(CONF_CURRENCY_NAME, default="usd"): str,
                vol.Optional(CONF_UNIT_OF_MEASUREMENT, default="$"): str,
                vol.Required(CONF_MULTIPLIER, default=1): cv.positive_int,
                vol.Required(CONF_UPDATE_FREQUENCY, default=60): cv.positive_float,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=cryptoinfo_schema,
            description_placeholders=PLACEHOLDERS,
        )
