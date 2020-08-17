import logging

CONF_CRYPTOCURRENCY_NAME = "cryptocurrency_name"
CONF_CURRENCY_NAME = "currency_name"
CONF_UPDATE_FREQUENCY = "update_frequency"
CONF_INCLUDE_24H_VOL = "include_24h_vol"
CONF_INCLUDE_24H_CHANGE = "include_24h_change"

SENSOR_PREFIX = "Cryptoinfo "
ATTR_LAST_UPDATE = "last_update"
ATTR_24H_CHANGE = "24h_change"
ATTR_24H_VOL = "24h_vol"

API_ENDPOINT = "https://api.coingecko.com/api/v3/"

_LOGGER = logging.getLogger(__name__)
