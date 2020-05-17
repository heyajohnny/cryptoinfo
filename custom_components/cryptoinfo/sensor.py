#!/usr/bin/env python3
"""
Sensor component for Cryptoinfo
Author: Johnny Visser

ToDo: Add properties:
-cryptocurrency_name,      (default = "bitcoin")
-currency_name,             (default = "usd")
-update_frequency           (default = 60) (value represent the number of minutes)
https://api.coingecko.com/api/v3/simple/price?ids=neo&vs_currencies=usd
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
    SENSOR_PREFIX,
    ATTR_LAST_UPDATE,
    API_ENDPOINT
)

SCAN_INTERVAL = timedelta(minutes=60)

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
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup Cryptoinfo sensor")

    cryptocurrency_name = config.get(CONF_CRYPTOCURRENCY_NAME).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    SCAN_INTERVAL = timedelta(minutes=(int(config.get(CONF_UPDATE_FREQUENCY).strip())))

    try:
        data = CryptoinfoData(cryptocurrency_name, currency_name)
        add_entities(CryptoinfoSensor(data, cryptocurrency_name, currency_name))
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False


class CryptoinfoData(object):
    def __init__(self, cryptocurrency_name, currency_name):
        self.data = None
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name

    @Throttle(SCAN_INTERVAL)
    def update(self):
        _LOGGER.warning("Updating Coingecko data")
        url = API_ENDPOINT + "simple/price?ids=" + self.cryptocurrency_name + "&vs_currencies=" + self.currency_name
        # sending get request
        r = requests.get(url=url)
        # extracting response json
        value = r.json()[self.cryptocurrency_name][self.currency_name]
        _LOGGER.warning(value)

        self.data = value


class CryptoinfoSensor(Entity):
    def __init__(self, data, cryptocurrency_name, currency_name):
        self.data = data
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
        self._name = SENSOR_PREFIX + "price"
        self._icon = "mdi:currency-usd"
        self._state = None
        self._last_update = None

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
    def device_state_attributes(self):
        return {ATTR_LAST_UPDATE: self._last_update}

    @Throttle(SCAN_INTERVAL)
    def update(self):
        self.data.update()
        price_data = self.data.data

        try:
            if price_data:
                # Set the values of the sensor
                self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
                self._state = price_data
            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
