#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo
Author: Johnny Visser

TODO: logic for the min_time_between_requests.
For every entry there's a coordinator.
The min_time_between_requests needs to be the time between the requests
of these coordinators. Maybe
create an id per entity (ascending integer/iterator starting at 0 + number of other entities).
keep track of the last updated time and last updated id. when the current time > last updated time and (the id > last id or if it was the highest id, the first id)
"""

import urllib.error
from datetime import date, datetime, timedelta
from typing import Any, Dict

from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const.const import (
    _LOGGER,
    API_ENDPOINT,
    ATTR_1H_CHANGE,
    ATTR_7D_CHANGE,
    ATTR_24H_CHANGE,
    ATTR_24H_VOLUME,
    ATTR_30D_CHANGE,
    ATTR_BASE_PRICE,
    ATTR_CIRCULATING_SUPPLY,
    ATTR_LAST_UPDATE,
    ATTR_MARKET_CAP,
    ATTR_MULTIPLIER,
    ATTR_TOTAL_SUPPLY,
    CONF_CRYPTOCURRENCY_NAMES,
    CONF_CURRENCY_NAME,
    CONF_ID,
    CONF_MIN_TIME_BETWEEN_REQUESTS,
    CONF_MULTIPLIERS,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    DOMAIN,
    SENSOR_PREFIX,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.warning("Setup Cryptoinfo sensor")

    config = config_entry.data

    id_name = config.get(CONF_ID)
    cryptocurrency_names = config.get(CONF_CRYPTOCURRENCY_NAMES).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT).strip()
    multipliers = config.get(CONF_MULTIPLIERS).strip()
    update_frequency = timedelta(minutes=(float(config.get(CONF_UPDATE_FREQUENCY))))

    # Create coordinator for centralized data fetching
    coordinator = CryptoDataCoordinator(
        hass, cryptocurrency_names, currency_name, update_frequency, id_name
    )

    # Wait for coordinator to do first update
    await coordinator.async_config_entry_first_refresh()

    entities = []
    crypto_list = [crypto.strip() for crypto in cryptocurrency_names.split(",")]
    multipliers_list = [multiplier.strip() for multiplier in multipliers.split(",")]

    multipliers_length = len(multipliers_list)
    crypto_list_length = len(crypto_list)

    if multipliers_length != crypto_list_length:
        _LOGGER.error(
            f"Length mismatch: multipliers ({multipliers_length}) and cryptocurrency names ({crypto_list_length}) must have the same length"
        )
        return False

    for i, cryptocurrency_name in enumerate(crypto_list):
        try:
            entities.append(
                CryptoinfoSensor(
                    coordinator,
                    cryptocurrency_name,
                    currency_name,
                    unit_of_measurement,
                    multipliers_list[i],
                    id_name,
                )
            )
        except urllib.error.HTTPError as error:
            _LOGGER.error(error.reason)
            return False

    async_add_entities(entities)


class CryptoDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        cryptocurrency_names: str,
        currency_name: str,
        update_frequency: timedelta,
        id_name: str,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name="Crypto Data",
            update_interval=update_frequency,
        )
        self.cryptocurrency_names = cryptocurrency_names
        self.currency_name = currency_name
        self.id_name = id_name

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        url = (
            f"{API_ENDPOINT}coins/markets"
            f"?ids={self.cryptocurrency_names}"
            f"&vs_currency={self.currency_name}"
            f"&price_change_percentage=1h%2C24h%2C7d%2C30d"
        )

        _LOGGER.warning(f"Fetch data from API endpoint: {self.id_name}")
        _LOGGER.warning(self.cryptocurrency_names)

        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return {coin["id"]: coin for coin in data}
        except Exception as err:
            _LOGGER.error(f"Error fetching data: {err}")
            raise


class CryptoinfoSensor(CoordinatorEntity):
    def __init__(
        self,
        coordinator: CryptoDataCoordinator,
        cryptocurrency_name: str,
        currency_name: str,
        unit_of_measurement: str,
        multiplier: str,
        id_name: str,
    ):
        super().__init__(coordinator)
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
        self._unit_of_measurement = unit_of_measurement
        self.multiplier = multiplier
        self._attr_device_class = SensorDeviceClass.MONETARY
        self.entity_id = "sensor." + (
            (SENSOR_PREFIX + (id_name + " " if len(id_name) > 0 else ""))
            .lower()
            .replace(" ", "_")
            + cryptocurrency_name
            + "_"
            + currency_name
            + "_"
            + multiplier
        )
        self._icon = "mdi:bitcoin"
        self._state_class = "measurement"
        self._attr_unique_id = (
            SENSOR_PREFIX
            + (id_name + " " if len(id_name) > 0 else "")
            + cryptocurrency_name
            + currency_name
            + multiplier
        )

    @property
    def icon(self):
        return self._icon

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.cryptocurrency_name in self.coordinator.data:
            return float(
                self.coordinator.data[self.cryptocurrency_name]["current_price"]
            ) * float(self.multiplier)
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if (
            not self.coordinator.data
            or self.cryptocurrency_name not in self.coordinator.data
        ):
            return {
                ATTR_LAST_UPDATE: datetime.today().strftime("%d-%m-%Y %H:%M"),
                ATTR_BASE_PRICE: None,
                ATTR_MULTIPLIER: None,
                ATTR_24H_VOLUME: None,
                ATTR_1H_CHANGE: None,
                ATTR_24H_CHANGE: None,
                ATTR_7D_CHANGE: None,
                ATTR_30D_CHANGE: None,
                ATTR_MARKET_CAP: None,
                ATTR_CIRCULATING_SUPPLY: None,
                ATTR_TOTAL_SUPPLY: None,
            }

        data = self.coordinator.data[self.cryptocurrency_name]
        return {
            ATTR_LAST_UPDATE: datetime.today().strftime("%d-%m-%Y %H:%M"),
            ATTR_BASE_PRICE: data["current_price"],
            ATTR_MULTIPLIER: self.multiplier,
            ATTR_24H_VOLUME: data["total_volume"],
            ATTR_1H_CHANGE: data["price_change_percentage_1h_in_currency"],
            ATTR_24H_CHANGE: data["price_change_percentage_24h_in_currency"],
            ATTR_7D_CHANGE: data["price_change_percentage_7d_in_currency"],
            ATTR_30D_CHANGE: data["price_change_percentage_30d_in_currency"],
            ATTR_MARKET_CAP: data["market_cap"],
            ATTR_CIRCULATING_SUPPLY: data["circulating_supply"],
            ATTR_TOTAL_SUPPLY: data["total_supply"],
        }
