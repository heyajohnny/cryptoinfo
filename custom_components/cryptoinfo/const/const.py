import logging

CONF_ID = "id"
CONF_CRYPTOCURRENCY_NAME = "cryptocurrency_name"
CONF_CURRENCY_NAME = "currency_name"
CONF_MULTIPLIER = "multiplier"
CONF_UPDATE_FREQUENCY = "update_frequency"

SENSOR_PREFIX = "homegecko "
ATTR_LAST_UPDATE = "last_update"
ATTR_VOLUME = "volume"
ATTR_BASE_PRICE = "baseprice"
ATTR_CHANGE = "change"
ATTR_MARKET_CAP = "market_cap"
ATTR_SYMBOL = "symbol"
ATTR_LOGO_URL = "logo_url"
ATTR_RANK = "rank"
ATTR_HIGH = "high"
ATTR_HIGH_TIMESTAMP = "high_timestamp"

API_ENDPOINT = "https://api.coingecko.com/api/v3/"

_LOGGER = logging.getLogger(__name__)
