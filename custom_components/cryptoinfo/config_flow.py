#!/usr/bin/env python3
"""
Config flow component for Cryptoinfo
Author: Johnny Visser
"""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .helper.crypto_info_data import CryptoInfoData

from .const.const import (
    _LOGGER,
    CONF_CRYPTOCURRENCY_NAMES,
    CONF_CURRENCY_NAME,
    CONF_ID,
    CONF_MIN_TIME_BETWEEN_REQUESTS,
    CONF_MULTIPLIER,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    DOMAIN,
)

PLACEHOLDERS = {
    "description_help": "For more information, see the <a href='https://github.com/heyajohnny/cryptoinfo' target='_blank'>documentation</a>.",
    "id_help": "Unique name for the sensor",
    "currency_name_help": "One of the currency names in <a href='https://api.coingecko.com/api/v3/simple/supported_vs_currencies' target='_blank'>this list</a>.",
    "cryptocurrency_names_help": "The 'id' values from one or more of the coins/tokens in <a href='https://api.coingecko.com/api/v3/coins/list' target='_blank'>this list</a>. seperated by , characters",
    "unit_of_measurement_help": "Do you want to use a currency symbol? (<a href='https://en.wikipedia.org/wiki/Currency_symbol#List_of_currency_symbols_currently_in_use' target='_blank'>Symbol list</a>)",
    "multiplier_help": "The number of coins/tokens",
    "update_frequency_help": "How often should the value be refreshed? Beware of the <a href='https://support.coingecko.com/hc/en-us/articles/4538771776153-What-is-the-rate-limit-for-CoinGecko-API-public-plan' target='_blank'>CoinGecko rate limit</a> when tracking multiple cryptocurrencies.",
    "min_time_between_requests_help": "The minimum time between the other entities and this entity to make a data request to the API. (This property is shared and the same for every entity)",
}


class CryptoInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_reconfigure(self, user_input: Mapping[str, Any] | None = None):
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry
        if user_input:
            # Update the shared data
            if DOMAIN in self.hass.data:
                self.hass.data[DOMAIN].min_time_between_requests = user_input[
                    CONF_MIN_TIME_BETWEEN_REQUESTS
                ]

            # Create new data combining old entry data with new user input
            new_data = {**entry.data, **user_input}

            # Update entry data
            self.hass.config_entries.async_update_entry(
                entry,
                data=new_data,
            )

            # Reload the entry
            await self.hass.config_entries.async_reload(entry.entry_id)

            return self.async_abort(reason="reconfigure_successful")

        return await self._redo_configuration(entry.data)

    async def _redo_configuration(self, entry_data: Mapping[str, Any]):
        # Get value from shared data if available
        default_min_time = 1.0
        if DOMAIN in self.hass.data:
            default_min_time = self.hass.data[DOMAIN].min_time_between_requests

        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(CONF_ID, default=entry_data[CONF_ID]): str,
                vol.Required(
                    CONF_CRYPTOCURRENCY_NAMES,
                    default=entry_data[CONF_CRYPTOCURRENCY_NAMES],
                ): str,
                vol.Required(
                    CONF_CURRENCY_NAME, default=entry_data[CONF_CURRENCY_NAME]
                ): str,
                vol.Required(
                    CONF_MULTIPLIER, default=entry_data[CONF_MULTIPLIER]
                ): cv.positive_int,
                vol.Optional(
                    CONF_UNIT_OF_MEASUREMENT,
                    default=entry_data[CONF_UNIT_OF_MEASUREMENT],
                ): str,
                vol.Required(
                    CONF_UPDATE_FREQUENCY, default=entry_data[CONF_UPDATE_FREQUENCY]
                ): cv.positive_float,
                vol.Required(
                    CONF_MIN_TIME_BETWEEN_REQUESTS,
                    default=default_min_time,
                ): cv.positive_float,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=cryptoinfo_schema,
            description_placeholders=PLACEHOLDERS,
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""
        errors = {}

        # Get default value from shared data if available
        default_min_time = 1.0
        if DOMAIN not in self.hass.data:
            # Initialize data if it doesn't exist
            self.hass.data[DOMAIN] = CryptoInfoData(self.hass)
            await self.hass.data[DOMAIN].async_initialize()

        default_min_time = self.hass.data[DOMAIN].min_time_between_requests

        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(CONF_ID, default="Main btc stash"): str,
                vol.Required(
                    CONF_CRYPTOCURRENCY_NAMES, default="bitcoin, ethereum"
                ): str,
                vol.Required(CONF_MULTIPLIER, default=1): cv.positive_int,
                vol.Required(CONF_CURRENCY_NAME, default="usd"): str,
                vol.Optional(CONF_UNIT_OF_MEASUREMENT, default="$"): str,
                vol.Required(CONF_UPDATE_FREQUENCY, default=60): cv.positive_float,
                vol.Required(
                    CONF_MIN_TIME_BETWEEN_REQUESTS, default=default_min_time
                ): cv.positive_float,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=cryptoinfo_schema,
                errors=errors,
                description_placeholders=PLACEHOLDERS,
            )

        try:
            # Validate the input
            await self.async_set_unique_id(user_input[CONF_ID])
            self._abort_if_unique_id_configured()

            # Update the shared min_time_between_requests
            self.hass.data[DOMAIN].min_time_between_requests = user_input[
                CONF_MIN_TIME_BETWEEN_REQUESTS
            ]

            # Create the config entry
            return self.async_create_entry(
                title=f"Cryptoinfo for {user_input[CONF_ID]}", data=user_input
            )

        except Exception as ex:
            _LOGGER.error(f"Error creating entry: {ex}")
            errors["base"] = f"Error creating entry: {ex}"
            return self.async_show_form(
                step_id="user",
                data_schema=cryptoinfo_schema,
                errors=errors,
                description_placeholders=PLACEHOLDERS,
            )
