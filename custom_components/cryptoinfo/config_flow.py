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
    CONF_CRYPTOCURRENCY_IDS,
    CONF_CURRENCY_NAME,
    CONF_ID,
    CONF_MIN_TIME_BETWEEN_REQUESTS,
    CONF_MULTIPLIERS,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    DOMAIN,
)


class CryptoInfoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _validate_input(self, user_input: dict[str, Any]) -> dict[str, Any]:
        """Validate the input."""
        errors = {}

        # Split and clean the values
        crypto_ids = [
            name.strip() for name in user_input[CONF_CRYPTOCURRENCY_IDS].split(",")
        ]
        multipliers = [mult.strip() for mult in user_input[CONF_MULTIPLIERS].split(",")]

        # Check if the counts match
        if len(crypto_ids) != len(multipliers):
            return {
                "base": "mismatch_values",
                "count_context": {
                    "crypto_count": len(crypto_ids),
                    "multiplier_count": len(multipliers),
                },
            }

        return errors

    async def async_step_reconfigure(self, user_input: Mapping[str, Any] | None = None):
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert entry
        if user_input:
            # Convert Mapping to dict to make it mutable
            user_input = dict(user_input)

            # Ensure empty strings are preserved for these optional properties
            if CONF_ID not in user_input:
                user_input[CONF_ID] = ""
            if CONF_UNIT_OF_MEASUREMENT not in user_input:
                user_input[CONF_UNIT_OF_MEASUREMENT] = ""

            # Validate the input
            validation_result = self._validate_input(user_input)
            if validation_result:
                count_context = validation_result.pop("count_context", {})
                return await self._redo_configuration(
                    entry.data, validation_result, count_context
                )

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

    async def _redo_configuration(
        self,
        entry_data: Mapping[str, Any],
        errors: dict[str, Any] | None = None,
        count_context: dict[str, Any] | None = None,
    ):
        if errors is None:
            errors = {}
        if count_context is None:
            count_context = {}

        # Get value from shared data if available
        default_min_time = 0.25
        if DOMAIN in self.hass.data:
            default_min_time = self.hass.data[DOMAIN].min_time_between_requests

        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ID,
                    description={"suggested_value": entry_data.get(CONF_ID, "")},
                ): str,
                vol.Required(
                    CONF_CRYPTOCURRENCY_IDS,
                    default=entry_data[CONF_CRYPTOCURRENCY_IDS],
                ): str,
                vol.Required(
                    CONF_CURRENCY_NAME, default=entry_data[CONF_CURRENCY_NAME]
                ): str,
                vol.Required(
                    CONF_MULTIPLIERS, default=entry_data[CONF_MULTIPLIERS]
                ): str,
                vol.Optional(
                    CONF_UNIT_OF_MEASUREMENT,
                    description={
                        "suggested_value": entry_data.get(CONF_UNIT_OF_MEASUREMENT, "")
                    },
                ): str,
                vol.Required(
                    CONF_UPDATE_FREQUENCY, default=entry_data[CONF_UPDATE_FREQUENCY]
                ): cv.positive_float,
                vol.Required(
                    CONF_MIN_TIME_BETWEEN_REQUESTS,
                    description={"suggested_value": default_min_time},
                ): cv.positive_float,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=cryptoinfo_schema,
            errors=errors,
            description_placeholders={**count_context},
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""
        errors = {}

        # Get default value from shared data if available
        default_min_time = 0.25
        if DOMAIN not in self.hass.data:
            # Initialize data if it doesn't exist
            self.hass.data[DOMAIN] = CryptoInfoData(self.hass)
            await self.hass.data[DOMAIN].async_initialize()

        default_min_time = self.hass.data[DOMAIN].min_time_between_requests

        # Use user_input values as defaults if they exist, otherwise use the original defaults
        defaults = {
            CONF_ID: "Main btc stash",
            CONF_CRYPTOCURRENCY_IDS: "bitcoin, ethereum",
            CONF_MULTIPLIERS: "1, 32",
            CONF_CURRENCY_NAME: "usd",
            CONF_UNIT_OF_MEASUREMENT: "$",
            CONF_UPDATE_FREQUENCY: 1,
            CONF_MIN_TIME_BETWEEN_REQUESTS: default_min_time,
        }

        # Update defaults with user input if it exists
        if user_input is not None:
            defaults.update(user_input)

        cryptoinfo_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_ID,
                    description={"suggested_value": defaults.get(CONF_ID, "")},
                ): str,
                vol.Required(
                    CONF_CRYPTOCURRENCY_IDS,
                    default=defaults[CONF_CRYPTOCURRENCY_IDS],
                ): str,
                vol.Required(CONF_MULTIPLIERS, default=defaults[CONF_MULTIPLIERS]): str,
                vol.Required(
                    CONF_CURRENCY_NAME, default=defaults[CONF_CURRENCY_NAME]
                ): str,
                vol.Optional(
                    CONF_UNIT_OF_MEASUREMENT,
                    description={
                        "suggested_value": defaults.get(CONF_UNIT_OF_MEASUREMENT, "")
                    },
                ): str,
                vol.Required(
                    CONF_UPDATE_FREQUENCY, default=defaults[CONF_UPDATE_FREQUENCY]
                ): cv.positive_float,
                vol.Required(
                    CONF_MIN_TIME_BETWEEN_REQUESTS,
                    default=defaults[CONF_MIN_TIME_BETWEEN_REQUESTS],
                ): cv.positive_float,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=cryptoinfo_schema, errors=errors
            )

        try:
            # Validate the input
            validation_result = self._validate_input(user_input)
            if validation_result:
                count_context = validation_result.pop("count_context", {})
                return self.async_show_form(
                    step_id="user",
                    data_schema=cryptoinfo_schema,
                    errors=validation_result,
                    description_placeholders={**count_context},
                )

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
                step_id="user", data_schema=cryptoinfo_schema, errors=errors
            )
