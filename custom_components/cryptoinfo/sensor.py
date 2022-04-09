#!/usr/bin/env python3
"""
Sensor component for Homegecko
Forked from Cryptoinfo by Johnny Visser
Author: McCookieM
"""

import requests
import voluptuous as vol
from datetime import datetime, date, timedelta
import urllib.error
from urllib.parse import urljoin, urlparse

from .const.const import (
    _LOGGER,
    CONF_CRYPTOCURRENCY_NAME,
    CONF_CURRENCY_NAME,
    CONF_MULTIPLIER,
    CONF_UPDATE_FREQUENCY,
    SENSOR_PREFIX,
    ATTR_LAST_UPDATE,
    ATTR_VOLUME,
    ATTR_BASE_PRICE,
    ATTR_MARKET_CAP,
    ATTR_SYMBOL,
    ATTR_LOGO_URL,
    ATTR_RANK,
    ATTR_HIGH,
    ATTR_HIGH_TIMESTAMP,
    ATTR_1_HR,
    ATTR_24_HR,
    ATTR_7_DAY,
    ATTR_30_DAY,
    ATTR_1_HR_PCT,
    ATTR_24_HR_PCT,
    ATTR_7_DAY_PCT,
    ATTR_30_DAY_PCT,
    API_ENDPOINT,
    CONF_ID,
)

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorDeviceClass
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CRYPTOCURRENCY_NAME, default="bitcoin"): cv.string,
        vol.Required(CONF_CURRENCY_NAME, default="usd"): cv.string,
        vol.Required(CONF_MULTIPLIER, default=1): cv.string,
        vol.Required(CONF_UPDATE_FREQUENCY, default=60): cv.string,
        vol.Optional(CONF_ID, default=""): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup Cryptoinfo sensor")

    id_name = config.get(CONF_ID)
    cryptocurrency_name = config.get(CONF_CRYPTOCURRENCY_NAME).lower().strip()
    currency_name = config.get(CONF_CURRENCY_NAME).strip()
    multiplier = config.get(CONF_MULTIPLIER).strip()
    update_frequency = timedelta(minutes=(int(config.get(CONF_UPDATE_FREQUENCY))))

    entities = []

    try:
        entities.append(
            CryptoinfoSensor(
                cryptocurrency_name,
                currency_name,
                multiplier,
                update_frequency,
                id_name,
            )
        )
    except urllib.error.HTTPError as error:
        _LOGGER.error(error.reason)
        return False

    add_entities(entities)


class CryptoinfoSensor(Entity):
    def __init__(
        self, cryptocurrency_name, currency_name, multiplier, update_frequency, id_name
    ):
        self.data = None
        self.cryptocurrency_name = cryptocurrency_name
        self.currency_name = currency_name
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
        self._volume = None
        self._base_price = None
        self._market_cap = None
        self._symbol = None
        self._logo_url = None
        self._rank = None
        self._high = None
        self._high_timestamp = None
        self._1_hr = None
        self._24_hr = None
        self._7_day = None
        self._30_day = None
        self._1_hr_pct = None
        self._24_hr_pct = None
        self._7_day_pct = None
        self._30_day_pct = None
        self._unit_of_measurement = currency_name.upper()
        self._attr_unique_id = cryptocurrency_name + currency_name + multiplier

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
    def extra_state_attributes(self):
        return {
            ATTR_LAST_UPDATE: self._last_update,
            ATTR_VOLUME: self._volume,
            ATTR_BASE_PRICE: self._base_price,
            ATTR_MARKET_CAP: self._market_cap,
            ATTR_SYMBOL: self._symbol,
            ATTR_LOGO_URL: self._logo_url,
            ATTR_RANK: self._rank,
            ATTR_HIGH: self._high,
            ATTR_HIGH_TIMESTAMP: self._high_timestamp,
            ATTR_1_HR: self._1_hr,
            ATTR_24_HR: self._24_hr,
            ATTR_7_DAY: self._7_day,
            ATTR_30_DAY: self._30_day,
            ATTR_1_HR: self._1_hr_pct,
            ATTR_24_HR: self._24_hr_pct,
            ATTR_7_DAY: self._7_day_pct,
            ATTR_30_DAY: self._30_day_pct,
        }
    def _update(self):
        url = (
            API_ENDPOINT
            + "coins/markets?ids="
            + self.cryptocurrency_name
            + "&vs_currency="
            + self.currency_name
        )
        # sending get request
        r = requests.get(url=url)
        # extracting response json
        self.data = r.json()[0]["current_price"]
        # multiply the price
        price_data = self.data * float(self.multiplier)

        try:
            if price_data:
                # Set the values of the sensor
                self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
                self._state = float(price_data)
                # set the attributes of the sensor
                self._volume = r.json()[0]["total_volume"]
                self._base_price = r.json()[0]["current_price"]
                self._market_cap = r.json()[0]["market_cap"]
                self._symbol = r.json()[0]["symbol"]
                self._logo_url = r.json()[0]["image"]
                self._rank = r.json()[0]["market_cap_rank"]
                self._high = r.json()[0]["ath"]
                high_dt = datetime.strptime(r.json()[0]["ath_date"],"%Y-%m-%dT%H:%M:%S.%fZ")
                self._high_timestamp = high_dt.strftime("%d-%m-%Y %H:%M")
                self._24_hr = r.json()[0]["price_change_24h"]
                self._24_hr_pct = r.json()[0]["price_change_percentage_24h"]

                 # Remove any query info from end of URL
                self._logo_url = urljoin(self._logo_url, urlparse(self._logo_url).path)
            else:
                raise ValueError()
        except ValueError:
            self._state = None
            self._last_update = datetime.today().strftime("%d-%m-%Y %H:%M")
            self._volume = None
            self._base_price = None
            self._market_cap = None
            self._symbol = None
            self._logo_url = None
            self._rank = None
            self._high = None
            self._high_timestamp = None
            self._high_timestamp = datetime(1970,1,1).strftime("%d-%m-%Y %H:%M")
            self._1_hr = None
            self._24_hr = None
            self._7_day = None
            self._30_day = None
            self._1_hr_pct = None
            self._24_hr_pct = None
            self._7_day_pct = None
            self._30_day_pct = None
