#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo
Author: Johnny Visser
"""

import urllib.error
from datetime import datetime, timedelta

from homeassistant import config_entries
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
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
    ATTR_14D_CHANGE,
    ATTR_24H_CHANGE,
    ATTR_24H_VOLUME,
    ATTR_30D_CHANGE,
    ATTR_1Y_CHANGE,
    ATTR_BASE_PRICE,
    ATTR_CIRCULATING_SUPPLY,
    ATTR_LAST_UPDATE,
    ATTR_CRYPTOCURRENCY_ID,
    ATTR_CRYPTOCURRENCY_NAME,
    ATTR_CRYPTOCURRENCY_SYMBOL,
    ATTR_CURRENCY_NAME,
    ATTR_MARKET_CAP,
    ATTR_MULTIPLIER,
    ATTR_TOTAL_SUPPLY,
    CONF_CRYPTOCURRENCY_IDS,
    CONF_CURRENCY_NAME,
    CONF_ID,
    CONF_MIN_TIME_BETWEEN_REQUESTS,
    CONF_MULTIPLIERS,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    SENSOR_PREFIX,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setup Cryptoinfo sensor")

    config = config_entry.data

    id_name = (config.get(CONF_ID) or "").strip()
    cryptocurrency_ids = config.get(CONF_CRYPTOCURRENCY_IDS).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    unit_of_measurement = (config.get(CONF_UNIT_OF_MEASUREMENT) or "").strip()
    multipliers = config.get(CONF_MULTIPLIERS).strip()
    update_frequency = timedelta(minutes=(float(config.get(CONF_UPDATE_FREQUENCY))))
    min_time_between_requests = timedelta(
        minutes=(float(config.get(CONF_MIN_TIME_BETWEEN_REQUESTS)))
    )

    # Create coordinator for centralized data fetching
    coordinator = CryptoDataCoordinator(
        hass,
        cryptocurrency_ids,
        currency_name,
        update_frequency,
        min_time_between_requests,
        id_name,
    )

    # Wait for coordinator to do first update
    await coordinator.async_config_entry_first_refresh()

    entities = []
    crypto_list = [crypto.strip() for crypto in cryptocurrency_ids.split(",")]
    multipliers_list = [multiplier.strip() for multiplier in multipliers.split(",")]

    multipliers_length = len(multipliers_list)
    crypto_list_length = len(crypto_list)

    if multipliers_length != crypto_list_length:
        _LOGGER.error(
            f"Length mismatch: multipliers ({multipliers_length}) and cryptocurrency id's ({crypto_list_length}) must have the same length"
        )
        return False

    for i, cryptocurrency_id in enumerate(crypto_list):
        try:
            entities.append(
                CryptoinfoSensor(
                    coordinator,
                    cryptocurrency_id,
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
    _active_coordinators = set()  # Set to track active coordinator IDs
    _instance_count = 0  # Class variable to track number of coordinators
    _last_update_time = None
    _last_updated_id = None

    def __init__(
        self,
        hass: HomeAssistant,
        cryptocurrency_ids: str,
        currency_name: str,
        update_frequency: timedelta,
        min_time_between_requests: timedelta,
        id_name: str,
    ):
        super().__init__(
            hass,
            _LOGGER,
            name="Crypto Data",
            update_interval=update_frequency,
        )
        self.instance_id = (
            CryptoDataCoordinator._instance_count
        )  # Assign current count as instance ID
        CryptoDataCoordinator._instance_count += 1  # Increment the counter
        CryptoDataCoordinator._active_coordinators.add(self.instance_id)
        self.cryptocurrency_ids = cryptocurrency_ids
        self.currency_name = currency_name
        self.id_name = id_name
        self.min_time_between_requests = min_time_between_requests
        self.update_frequency = update_frequency

    async def async_will_remove_from_hass(self) -> None:
        """Handle removal from Home Assistant."""
        _LOGGER.debug(f"Removing coordinator {self.instance_id}")
        CryptoDataCoordinator._active_coordinators.discard(self.instance_id)
        # If this was the last updated ID, reset it
        if CryptoDataCoordinator._last_updated_id == self.instance_id:
            CryptoDataCoordinator._last_updated_id = None

    async def _async_update_data(self):
        """Fetch data from API endpoint with coordinated timing."""
        current_time = datetime.now()

        # If this is the first ever request, fetch data immediately
        if CryptoDataCoordinator._last_update_time is None:
            CryptoDataCoordinator._last_update_time = current_time
            CryptoDataCoordinator._last_updated_id = self.instance_id

            _LOGGER.debug(
                f"First request, fetching data for sensor: {self.id_name} instance_id: {self.instance_id} cryptocurrency_ids: {self.cryptocurrency_ids}"
            )

            url = (
                f"{API_ENDPOINT}coins/markets"
                f"?ids={self.cryptocurrency_ids}"
                f"&vs_currency={self.currency_name}"
                f"&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C1y"
            )

            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return {coin["id"]: coin for coin in data}
            except Exception as err:
                _LOGGER.error(f"Error fetching data: {err}")
                return None

        time_since_last_request = current_time - CryptoDataCoordinator._last_update_time

        if (
            time_since_last_request + timedelta(seconds=1)
            < self.min_time_between_requests
        ):
            _LOGGER.debug(
                f"Not enough time has passed {self.instance_id} {self.min_time_between_requests} "
                f"waiting for time between requests {time_since_last_request} frequency:{self.update_frequency}"
            )
            return self.data if self.data else None

        # Find the next active coordinator ID
        last_id = CryptoDataCoordinator._last_updated_id
        _LOGGER.debug(
            f"Last id {last_id}, Active coordinators: {sorted(CryptoDataCoordinator._active_coordinators)}"
        )

        if last_id is None or last_id not in CryptoDataCoordinator._active_coordinators:
            should_update = self.instance_id == min(
                CryptoDataCoordinator._active_coordinators
            )
        else:
            # Get sorted list of active coordinators
            active_ids = sorted(CryptoDataCoordinator._active_coordinators)
            current_index = active_ids.index(last_id)
            next_index = (current_index + 1) % len(active_ids)
            next_id = active_ids[next_index]
            should_update = self.instance_id == next_id
            _LOGGER.debug(f"next_id {next_id}")

        if not should_update:
            _LOGGER.debug(f"Coordinator {self.instance_id} waiting for turn")
            return self.data if self.data else None

        _LOGGER.debug(
            f"Fetch data from API endpoint, sensor: {self.id_name} instance_id: {self.instance_id} cryptocurrency_ids: {self.cryptocurrency_ids}"
        )

        url = (
            f"{API_ENDPOINT}coins/markets"
            f"?ids={self.cryptocurrency_ids}"
            f"&vs_currency={self.currency_name}"
            f"&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C1y"
        )

        try:
            session = aiohttp_client.async_get_clientsession(self.hass)
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                # Update the last update time and ID only after successful request
                CryptoDataCoordinator._last_update_time = current_time
                CryptoDataCoordinator._last_updated_id = self.instance_id

                return {coin["id"]: coin for coin in data}
        except Exception as err:
            _LOGGER.error(f"Error fetching data: {err}")


class CryptoinfoSensor(CoordinatorEntity):
    def __init__(
        self,
        coordinator: CryptoDataCoordinator,
        cryptocurrency_id: str,
        currency_name: str,
        unit_of_measurement: str,
        multiplier: str,
        id_name: str,
    ):
        super().__init__(coordinator)
        self.cryptocurrency_id = cryptocurrency_id
        self.currency_name = currency_name
        self._unit_of_measurement = unit_of_measurement
        self.multiplier = multiplier
        self._attr_device_class = SensorDeviceClass.MONETARY
        self.entity_id = "sensor." + (
            (SENSOR_PREFIX + (id_name + " " if len(id_name) > 0 else ""))
            .lower()
            .replace(" ", "_")
            + cryptocurrency_id
            + "_"
            + currency_name
        )
        self._icon = "mdi:bitcoin"
        self._state_class = "measurement"
        self._attr_unique_id = (
            SENSOR_PREFIX
            + (id_name + " " if len(id_name) > 0 else "")
            + cryptocurrency_id
            + currency_name
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
        if self.coordinator.data and self.cryptocurrency_id in self.coordinator.data:
            return float(
                self.coordinator.data[self.cryptocurrency_id]["current_price"]
            ) * float(self.multiplier)
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if (
            not self.coordinator.data
            or self.cryptocurrency_id not in self.coordinator.data
        ):
            return {
                ATTR_LAST_UPDATE: datetime.today().strftime("%d-%m-%Y %H:%M"),
                ATTR_CRYPTOCURRENCY_NAME: None,
                ATTR_CURRENCY_NAME: None,
                ATTR_BASE_PRICE: None,
                ATTR_MULTIPLIER: None,
                ATTR_24H_VOLUME: None,
                ATTR_1H_CHANGE: None,
                ATTR_24H_CHANGE: None,
                ATTR_7D_CHANGE: None,
                ATTR_14D_CHANGE: None,
                ATTR_30D_CHANGE: None,
                ATTR_1Y_CHANGE: None,
                ATTR_MARKET_CAP: None,
                ATTR_CIRCULATING_SUPPLY: None,
                ATTR_TOTAL_SUPPLY: None,
            }

        data = self.coordinator.data[self.cryptocurrency_id]
        return {
            ATTR_LAST_UPDATE: datetime.today().strftime("%d-%m-%Y %H:%M"),
            ATTR_CRYPTOCURRENCY_ID: self.cryptocurrency_id,
            ATTR_CRYPTOCURRENCY_NAME: data["name"],
            ATTR_CRYPTOCURRENCY_SYMBOL: data["symbol"],
            ATTR_CURRENCY_NAME: self.currency_name,
            ATTR_BASE_PRICE: data["current_price"],
            ATTR_MULTIPLIER: self.multiplier,
            ATTR_24H_VOLUME: data["total_volume"],
            ATTR_1H_CHANGE: data["price_change_percentage_1h_in_currency"],
            ATTR_24H_CHANGE: data["price_change_percentage_24h_in_currency"],
            ATTR_7D_CHANGE: data["price_change_percentage_7d_in_currency"],
            ATTR_14D_CHANGE: data["price_change_percentage_14d_in_currency"],
            ATTR_30D_CHANGE: data["price_change_percentage_30d_in_currency"],
            ATTR_1Y_CHANGE: data["price_change_percentage_1y_in_currency"],
            ATTR_MARKET_CAP: data["market_cap"],
            ATTR_CIRCULATING_SUPPLY: data["circulating_supply"],
            ATTR_TOTAL_SUPPLY: data["total_supply"],
        }

    async def async_will_remove_from_hass(self) -> None:
        """Handle removal from Home Assistant."""
        await self.coordinator.async_will_remove_from_hass()  # type: ignore
        await super().async_will_remove_from_hass()
