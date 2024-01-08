# Coin Display
Displays prices of configured cryptocurrencys sourced from CoinGecko.
Based on [Spotipy Display](https://github.com/jedclarin/spotipy-display).

![coin-display](https://github.com/janclarin/coin-display/assets/2449384/277d0103-f1dc-4639-9d7a-f1567b65f292)

## Features
- Displays configured cryptocurrency prices for configured coins
- Bottom (KEY4) button triggers price refresh

## Hardware
- Raspberry Pi 4
- Raspberry Pi OS Lite 64-bit
- [Waveshare 2.7" e-Paper Display GPIO HAT](https://www.amazon.com/2-7inch-HAT-Resolution-Electronic-Communicating/dp/B075FQKSZ9/ref=sr_1_2?crid=3QTGQC71HK2NP&keywords=waveshare+2.7&qid=1704703657&sprefix=waveshare+2.7%2Caps%2C161&sr=8-2)

## Setup

### Get CoinGecko API key
Get an API key for retrieving crypto prices.
1. Create a [CoinGecko](https://www.coingecko.com) account
2. Create a Demo Account (use browser find to find the small button)
3. Note down the API Key in the [developer dashboard](https://www.coingecko.com/en/developers/dashboard)

### Configure Raspberry Pi
Turn on SPI after attaching e-paper display to Pi via GPIO.
1. Open Raspberry Pi config: `sudo raspi-config`
2. Choose Interfacing Options -> SPI -> Yes Enable SPI interface
3. Save config changes
4. Reboot Pi: `sudo reboot`

### Install dependencies
1. Create a `.env` file based on `.env.example` with your CoinGecko API key
    - `COINGECKO_CSV_IDS`: comma-separated string of CoinGecko API IDs found on a coin's page
    - `COINGECKO_DEMO_API_KEY`: API key from CoinGecko developer dashboard
    - `REFRESH_INTERVAL_MINS`: time interval in minutes between automatically refreshing prices
    - `PERCENT_TIME_COLUMN_[1|2|3]`: the time window price percent change change, `1h, 24h, 7d, 14d, 30d, 200d, 1y` 
2. Set up virtual environment: `python3 -m venv venv`
3. Activate virtualenv: `source venv/bin/activate`
4. Install dependencies: `pip3 install lgpio gpiozero numpy Pillow requests RPi.GPIO spidev`

### Test it out
Before configuring `spotipy-display` to run automatically, test it first.
1. Activate virtualenv: `source venv/bin/activate`
2. Run: `python3 main.py`
3. After confirming that it works, quit with <kbd>CTRL+C</kbd>

### Run on reboot
1. Add systemctl service: `sudo vim /etc/systemd/system/coin-display.service`
    ```
    [Unit]
    Description=Coin Display
    After=network.target

    [Service]
    ExecStart=/home/pi/coin-display/venv/bin/python3 /home/pi/coin-display/main.py
    WorkingDirectory=/home/pi/coin-display
    Restart=always
    User=pi
    Group=pi
    Environment=PATH=/home/pi/coin-display/venv/bin:/usr/bin:$PATH

    [Install]
    WantedBy=multi-user.target
    ```
2. Reload systemctl: `sudo systemctl daemon-reload`
3. Enable `coin-display`: `sudo systemctl enable coin-display.service`
4. Start `coin-display`: `sudo systemctl start coin-display.service`
5. Monitor logs: `sudo journalctl -fu coin-display.service`
6. Reboot Pi to ensure everything works