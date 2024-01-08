# Coin Display
Displays prices of configured cryptocurrencys sourced from CoinGecko.
Based on [Spotipy Display](https://github.com/jedclarin/spotipy-display).

## Features
- Displays configured cryptocurrency prices for configured coins
- Bottom (KEY4) button triggers price refresh

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