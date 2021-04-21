## Home Assistant sensor component for cryptocurrencies
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
### Powered by CoinGecko API

#### Provides Home Assistant sensors for all cryptocurrencies supported by CoinGecko

If you like my work, please buy me a coffee. This will keep me awake :)

<a href="https://www.buymeacoffee.com/1v3ckWD" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

### Install:
- Copy the files in the /custom_components/cryptoinfo/ folder to: [homeassistant]/config/custom_components/cryptoinfo/

Example config:
```Configuration.yaml:
  sensor:
    - platform: cryptoinfo
      id: "main wallet"                (optional, default = '') add some extra naming to the sensor
      cryptocurrency_name: "ethereum"  (default = "bitcoin")
      currency_name: "eur"             (default = "usd")
      multiplier: 1                    (default = 1) the currency value multiplied by this number
      update_frequency: 15             (default = 60) number of minutes to refresh data of the sensor
```
Or copy paste the values from this [configuration.yaml](https://github.com/heyajohnny/cryptoinfo/blob/master/example/configuration.yaml)

For the complete list of supported values for 'cryptocurrency_name', visit this page:
https://api.coingecko.com/api/v3/coins/list and copy / paste the "id" value to use as 'cryptocurrency_name'

For the complete list of supported values for 'currency_name', visit this page:
https://api.coingecko.com/api/v3/simple/supported_vs_currencies and copy / paste the value to use as 'currency_name'

### Attributes
There are 3 important attributes:
- volume.       This will return the 24 hour volume in 'currency_name'(default = "usd") of the 'cryptocurrency_name'(default = "bitcoin")
- change.       This will return the 24 hour change in 'currency_name'(default = "usd") of the 'cryptocurrency_name'(default = "bitcoin")
- market_cap.   This will return the total market cap of the 'cryptocurrency_name'(default = "bitcoin") displayed in 'currency_name'(default = "usd")

Example for usage of attributes.
This example creates a new sensor with the attribute value 'vokume' of the sensor 'sensor.cryptoinfo_main_wallet_ethereum_eur':
```yaml
- platform: template
    sensors:
      cryptoinfo_main_wallet_ethereum_eur_24h_volume:
        value_template: "{{ state_attr('sensor.cryptoinfo_main_wallet_ethereum_eur', 'volume') | round(0) }}"
        unit_of_measurement: "€"
```


If you want to know the total value of your cryptocurrencies, you could use this template as an example.
This example combines the total value of 3 sensors into this 1 template sensor:
```yaml
  - platform: template
    sensors:
      crypto_total:
        value_template: "{{
          ( states('sensor.cryptoinfo_main_wallet_ethereum_eur') | float | round(2)) +
          ( states('sensor.cryptoinfo_bitcoin_eur') | float | round(2)) +
          ( states('sensor.cryptoinfo_cardano_eur') | float | round(2))
          }}"
        unit_of_measurement: '€'
        friendly_name: Total value of all my cryptocurrencies
```

### Issues and new functionality
If there are any problems, please create an issue in https://github.com/heyajohnny/cryptoinfo/issues
If you want new functionality added, please create an issue with a description of the new functionality that you want in: https://github.com/heyajohnny/cryptoinfo/issues

