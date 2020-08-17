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
      cryptocurrency_name: "ethereum"  (default = "bitcoin")
      currency_name: "eur"             (default = "usd")
      update_frequency: 15             (default = 60) number of minutes to refresh data of the sensor
      include_24h_vol: True             (default = False) Add attribute with 24h Volume
      include_24h_change: True             (default = False)  Add attribute with 24h change in %
```

For the complete list of supported values for 'cryptocurrency_name', visit this page:
https://api.coingecko.com/api/v3/coins/list and copy / paste the "id" value to use as 'cryptocurrency_name'

For the complete list of supported values for 'currency_name', visit this page:
https://api.coingecko.com/api/v3/simple/supported_vs_currencies and copy / paste the value to use as 'currency_name'

### Issues and new functionality
If there are any problems, please create an issue in https://github.com/heyajohnny/cryptoinfo/issues
If you want new functionality added, please create an issue with a description of the new functionality that you want in: https://github.com/heyajohnny/cryptoinfo/issues

