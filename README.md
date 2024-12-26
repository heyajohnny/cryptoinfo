## Home Assistant sensor component for cryptocurrencies
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

![icon_mini](https://github.com/user-attachments/assets/328f93d8-6ea7-4877-bc31-1c5b33c4583a)
### Powered by CoinGecko API

#### Provides Home Assistant sensors for all cryptocurrencies supported by CoinGecko

## Breaking changes for upgrading from v0.x.x to v1.x.x
If you've just updated from v0.x.x to v1.x.x please remove the cryptoinfo sensor from your configuration.yaml and follow [Installation step 2](#installation-step-2)

If you like my work, please buy me a coffee or donate some crypto currencies. This will keep me awake, asleep, or whatever :wink:

<a href="https://www.buymeacoffee.com/1v3ckWD" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a><details>
  <summary>Crypto currency addresses</summary>
<img width="164px" alt="xmr" src="https://user-images.githubusercontent.com/20553716/210132784-63613225-d9da-427d-a20b-e1003045a1f4.png">
<img width="164px" alt="btc" src="https://user-images.githubusercontent.com/20553716/210132426-6c58d8d1-b351-4ae7-9b61-cd5511cdb4ed.png">
<img width="164px" alt="ada" src="https://user-images.githubusercontent.com/20553716/210132510-b1106b55-c9e3-413d-b8e0-26ba4e24a5de.png">
</details>

If you need more advanced features than this project offers, see [Cryptoinfo Advanced](https://github.com/TheHolyRoger/hass-cryptoinfo)

### Installation step 1:
There are 2 ways to install cryptoinfo:
1. Download 'cryptoinfo' from the HACS store
2. Copy the files in the /custom_components/cryptoinfo/ folder to: [homeassistant]/config/custom_components/cryptoinfo/

### Installation step 2
The next step is to add cryptoinfo sensors to your Home Assistant:
1. Browse to your Home Assistant config page
2. Press Settings --> Devices & Services

![image](https://github.com/user-attachments/assets/c4812206-835e-4239-9757-8645ae6c772b)

3. Press 'Add Integration' and search for 'cryptoinfo' and select the 'cryptoinfo' integration

![image](https://github.com/user-attachments/assets/83e3e165-61fa-4aa9-8421-9fc019bfae82)

4. Fill in the 'add new sensor' form

![image](https://github.com/user-attachments/assets/d76156df-dc2c-4f5f-bbdf-ea58570c5963)

### Properties
<pre>
- Identifier                                Unique name for the sensor
- Cryptocurrency id's                       One or more of the 'id' values (seperated by a , character) that you can find on this <a href='https://api.coingecko.com/api/v3/coins/list' target='_blank'>page</a>
- Multipliers                               The number of coins/tokens (seperated by a , character). The number of Multipliers must match the number of Cryptocurrency id's
- Currency name                             One of the currency names that you can find on this <a href='https://api.coingecko.com/api/v3/simple/supported_vs_currencies' target='_blank'>page</a>
- Unit of measurement                       You can use a currency symbol or you can make it empty. You can find some symbols on this <a href='https://en.wikipedia.org/wiki/Currency_symbol#List_of_currency_symbols_currently_in_use' target='_blank'>page</a>
- Update frequency (minutes)                How often should the value be refreshed? Beware of the <a href='https://support.coingecko.com/hc/en-us/articles/4538771776153-What-is-the-rate-limit-for-CoinGecko-API-public-plan' target='_blank'>CoinGecko rate limit</a> when using multiple sensors
- Minimum time between requests (minutes)   The minimum time between the other sensors and this sensor to make a data request to the API. (This property is shared and the same for every sensor). You can set this value to 0 if you only use 1 sensor
</pre>

### Attributes
The entities have some important attributes:
```
- last_update           This will return the date and time of the last update
- cryptocurrency_id     This will return the cryptocurrency id
- cryptocurrency_name   This will return the cryptocurrency name
- cryptocurrency_symbol This will return the cryptocurrency symbol
- currency_name         This will return the currency name
- base_price            This will return the price of 1 coin / token in 'currency_name'(default = "usd") of the 'cryptocurrency_id'
- multiplier            This will return the number of coins / tokens
- 24h_volume            This will return the 24 hour volume in 'currency_name'(default = "usd") of the 'cryptocurrency_id'(default = "bitcoin")
- 1h_change             This will return the 1 hour change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- 24h_change            This will return the 24 hour change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- 7d_change             This will return the 7 day change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- 14d_change            This will return the 14 day change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- 30d_change            This will return the 30 day change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- 1y_change             This will return the 1 year change in percentage of the 'cryptocurrency_id'(default = "bitcoin")
- market_cap            This will return the total market cap of the 'cryptocurrency_id'(default = "bitcoin") displayed in 'currency_name'(default = "usd")
- circulating_supply    This will return the circulating supply of the 'cryptocurrency_id'(default = "bitcoin")
- total_supply          This will return the total supply of the 'cryptocurrency_id'(default = "bitcoin")
- ath_price             This will return the All Time High Price of the ''currency_name'(default = "usd") of the 'cryptocurrency_id'(default = "bitcoin")'
- ath_date              This will return the date when the All Time High was reached of the ''currency_name'(default = "usd") of the 'cryptocurrency_id'(default = "bitcoin")'
- ath_change This will return the percentage change from the All Time High of the ''currency_name'(default = "usd") of the 'cryptocurrency_id'(default = "bitcoin")'
```

Template example for usage of attributes.
This example creates a new sensor with the attribute value '24h_volume' of the sensor 'sensor.cryptoinfo_main_wallet_ethereum_eur':
```yaml
  - platform: template
    sensors:
      cryptoinfo_main_wallet_ethereum_eur_24h_volume:
        value_template: "{{ state_attr('sensor.cryptoinfo_main_wallet_ethereum_eur', '24h_volume') | float(0) | round(0) }}"
        unit_of_measurement: "€"
```

If you want to know the total value of your cryptocurrencies, you could use this template as an example.
This example combines the total value of all your sensors into this 1 template sensor:
```yaml
  - platform: template
    sensors:
      crypto_total:
        value_template: >
          {{ integration_entities('cryptoinfo')
              | map('states')
              | map('float', 0)
              | sum | round(2) }}
        unit_of_measurement: >
          {{ expand(integration_entities('cryptoinfo'))
              | map(attribute='attributes.unit_of_measurement')
              | list | default(['$'], true)
              | first }}
        friendly_name: Total value of all my cryptocurrencies
```

### API limit
CoinGecko’s Public API has a <a href='https://support.coingecko.com/hc/en-us/articles/4538771776153-What-is-the-rate-limit-for-CoinGecko-API-public-plan' target='_blank'>rate limit</a> of 5 to 15 calls per minute, depending on usage conditions worldwide.

### Issues and new functionality
If there are any problems, please create an issue in https://github.com/heyajohnny/cryptoinfo/issues
If you want new functionality added, please create an issue with a description of the new functionality that you want in: https://github.com/heyajohnny/cryptoinfo/issues
