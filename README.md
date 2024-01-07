# Coin Display
Displays prices of configured cryptocurrencys sourced from CoinGecko.
Based on [Spotipy Display](https://github.com/jedclarin/spotipy-display).

## Setup

### Configure Raspberry Pi
Turn on SPI after attaching e-paper display to Pi via GPIO.
1. Open Raspberry Pi config: `sudo raspi-config`
2. Choose Interfacing Options -> SPI -> Yes Enable SPI interface
3. Save config changes
4. Reboot Pi: `sudo reboot`