#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo
Author: Johnny Visser

ToDo:
- Add documentation and reference to coingecko
"""

import requests
import voluptuous as vol
from datetime import datetime, date, timedelta
import urllib.error

from .const.const import (
    _LOGGER,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_UPDATE_FREQUENCY,
    CONF_INCLUDE_24H_VOL,
    CONF_INCLUDE_24H_CHANGE,
    SENSOR_PREFIX,
    ATTR_LAST_UPDATE,
    ATTR_24H_VOL,
    ATTR_24H_CHANGE,
    API_ENDPOINT,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCES
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CRYPTOCURRENCY_NAME, default="bitcoin"): cv.string,
        vol.Required(CONF_CURRENCY_NAME, default="usd"): cv.string,
        vol.Required(CONF_UPDATE_FREQUENCY, default=60): cv.string,
        vol.Required(CONF_INCLUDE_24H_VOL, default=False): cv.boolean,
        vol.Required(CONF_INCLUDE_24H_CHANGE, default=False): cv.boolean,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup Cryptoinfo sensor")

    cryptocurrency_name = config.get(CONF_CRYPTOCURRENCY_NAME).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    update_frequency = timedelta(minutes=(int(config.get(CONF_UPDATE_FREQUENCY))))
    include_24hr_vol = config.get(CONF_INCLUDE_24H_VOL)
    include_24hr_change = config.get(CONF_INCLUDE_24H_CHANGE)
    
    entities = []

    try:
        data = CryptoinfoData(cryptocurrency_name, currency_name, update_frequency, include_24hr_vol, include_24hr_change)
        entities.append(
            CryptoinfoSensor(data, cryptocurrency_name, currency_name, update_frequency, include_24hr_vol, include_24hr_change)
        )
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    add_entities(entities)


class CryptoinfoData(object):
    def __init__(self, cryptocurrency_name, currency_name, update_frequency, include_24hr_vol, include_24hr_change):
        self.data = None
        self.market_cap = None
        self.vol_24h = None
        self.change_24h = None
        self.include_24hr_vol = include_24hr_vol
        self.include_24hr_change = include_24hr_change
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
        self.update = Throttle(update_frequency)(self._update)

    def _update(self):
        _LOGGER.debug("Updating Coingecko data")
        url = (
            API_ENDPOINT
            + "simple/price?ids="
            + self.cryptocurrency_name
            + "&vs_currencies="
            + self.currency_name
            + "&include_24hr_vol="
            + str(self.include_24hr_vol).lower()
            + "&include_24hr_change="
            + str(self.include_24hr_change).lower()
        )
        _LOGGER.warning(url)
        # sending get request
        r = requests.get(url=url)
        # extracting response json
        value = r.json()[self.cryptocurrency_name][self.currency_name]
        _LOGGER.warning(r.json())
        if self.include_24hr_vol:
            self.vol_24h = r.json()[self.cryptocurrency_name][self.currency_name + "_24h_vol"]
        if self.include_24hr_change:
            self.change_24h = r.json()[self.cryptocurrency_name][self.currency_name + "_24h_change"]
        _LOGGER.warning(self.change_24h)
        self.data = value


class CryptoinfoSensor(Entity):
    def __init__(self, data, cryptocurrency_name, currency_name, update_frequency, include_24hr_vol, include_24hr_change):
        self.data = data
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
        self.update = Throttle(update_frequency)(self._update)
        self._name = SENSOR_PREFIX + cryptocurrency_name + " " + currency_name
        self._icon = "mdi:bitcoin"
        self._state = None
        self._last_update = None
        self._24h_vol = None
        self._24h_change = None
        self._unit_of_measurement = "\u200b"
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        return self._attributes

    def _update(self):
        self.data.update()
        price_data = self.data.data
        change = self.data.change_24h
        vol = self.data.vol_24h
        try:
            if vol:
                self._24h_vol = int(vol)
                self._attributes[ATTR_24H_VOL] = self._24h_vol
            else:
                raise ValueError()
        except ValueError:
            self._24h_vol = None
        try:
            if change:
                self._24h_change = round(float(change),2)
                self._attributes[ATTR_24H_CHANGE] = self._24h_change
            else:
                raise ValueError()
        except ValueError:
            self._24h_change = None
        try:
            if price_data:
                # Set the values of the sensor
                self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
                self._attributes[ATTR_LAST_UPDATE] = self._last_update
                self._state = float(price_data)

            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
