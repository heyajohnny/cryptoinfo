#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo
Author: Johnny Visser
"""

import requests
import voluptuous as vol
from datetime import datetime, date, timedelta
import urllib.error

from .const.const import (
    _LOGGER,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_MULTIPLIER,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_UPDATE_FREQUENCY,
    SENSOR_PREFIX,
    ATTR_LAST_UPDATE,
    ATTR_24H_VOLUME,
    ATTR_BASE_PRICE,
    ATTR_1H_CHANGE,
    ATTR_24H_CHANGE,
    ATTR_7D_CHANGE,
    ATTR_30D_CHANGE,
    ATTR_MARKET_CAP,
    ATTR_CIRCULATING_SUPPLY,
    ATTR_TOTAL_SUPPLY,
    API_ENDPOINT,
    CONF_ID,
)

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    _LOGGER.debug("Setup Cryptoinfo sensor")

    config = config_entry.data

    id_name = config.get(CONF_ID)
    cryptocurrency_name = config.get(CONF_CRYPTOCURRENCY_NAME).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT).strip()
    multiplier = config.get(CONF_MULTIPLIER)
    update_frequency = timedelta(minutes=(float(config.get(CONF_UPDATE_FREQUENCY))))

    entities = []

    try:
        entities.append(
            CryptoinfoSensor(
                cryptocurrency_name,
                currency_name,
                unit_of_measurement,
                multiplier,
                update_frequency,
                id_name,
            )
        )
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    async_add_entities(entities)


class CryptoinfoSensor(Entity):
    def __init__(
        self,
        cryptocurrency_name,
        currency_name,
        unit_of_measurement,
        multiplier,
        update_frequency,
        id_name,
    ):
        self.data = None
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
        self._unit_of_measurement = unit_of_measurement
        self.multiplier = multiplier
        self.update = Throttle(update_frequency)(self._update)
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._name = (
            SENSOR_PREFIX
            + (id_name + " " if len(id_name) > 0 else "")
            + cryptocurrency_name
            + " "
            + currency_name
        )
        self._icon = "mdi:bitcoin"
        self._state = None
        self._last_update = None
        self._base_price = None
        self._24h_volume = None
        self._1h_change = None
        self._24h_change = None
        self._7d_change = None
        self._30d_change = None
        self._market_cap = None
        self._circulating_supply = None
        self._total_supply = None
        self._state_class = "measurement"
        self._attr_unique_id = cryptocurrency_name + currency_name + str(multiplier)

    @property
    def name(self):
        return self._name

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
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            ATTR_LAST_UPDATE: self._last_update,
            ATTR_BASE_PRICE: self._base_price,
            ATTR_24H_VOLUME: self._24h_volume,
            ATTR_1H_CHANGE: self._1h_change,
            ATTR_24H_CHANGE: self._24h_change,
            ATTR_7D_CHANGE: self._7d_change,
            ATTR_30D_CHANGE: self._30d_change,
            ATTR_MARKET_CAP: self._market_cap,
            ATTR_CIRCULATING_SUPPLY: self._circulating_supply,
            ATTR_TOTAL_SUPPLY: self._total_supply,
        }

    def _update(self):
        url = (
            API_ENDPOINT
            + "coins/markets?ids="
            + self.cryptocurrency_name
            + "&vs_currency="
            + self.currency_name
            + "&page=1&sparkline=false&price_change_percentage=1h%2C24h%2C7d%2C30d"
        )
        r = None
        try:
            # sending get request
            r = requests.get(url=url)
            # extracting response json
            self.data = r.json()[0]
            # multiply the price
            price_data = self.data["current_price"] * float(self.multiplier)
        except Exception as error:
            _LOGGER.error(
                "Error fetching update from coingecko: "
                + str(error)
                + " - response status: "
                + str(r.status_code if r is not None else None)
                + " - "
                + str(r.reason if r is not None else None)
            )
            price_data = None

        try:
            if price_data:
                # Set the values of the sensor
                self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
                self._state = float(price_data)
                # set the attributes of the sensor
                self._base_price = r.json()[0]["current_price"]
                self._24h_volume = r.json()[0]["total_volume"]
                self._1h_change = r.json()[0]["price_change_percentage_1h_in_currency"]
                self._24h_change = r.json()[0][
                    "price_change_percentage_24h_in_currency"
                ]
                self._7d_change = r.json()[0]["price_change_percentage_7d_in_currency"]
                self._30d_change = r.json()[0][
                    "price_change_percentage_30d_in_currency"
                ]
                self._market_cap = r.json()[0]["market_cap"]
                self._circulating_supply = r.json()[0]["circulating_supply"]
                self._total_supply = r.json()[0]["total_supply"]
            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
            self._base_price = None
            self._24h_volume = None
            self._1h_change = None
            self._24h_change = None
            self._7d_change = None
            self._30d_change = None
            self._market_cap = None
            self._circulating_supply = None
            self._total_supply = None
