import os
from email import message
from PIL import Image, ImageDraw, ImageFont
import os
import logging
import epd2in7_V2
import time
import RPi.GPIO as GPIO
import time
from dotenv import load_dotenv
import requests
import threading
import epd2in7_V2

load_dotenv()
logging.basicConfig(level=logging.INFO)

KEY_1 = 5
KEY_2 = 6
KEY_3 = 13
KEY_4 = 19
PADDING = 4
PERCENT_DECIMALS = 2

COINGECKO_CSV_IDS=os.environ.get("COINGECKO_CSV_IDS")
COINGECKO_DEMO_API_KEY=os.environ.get("COINGECKO_DEMO_API_KEY")
REFRESH_INTERVAL_MINS=int(os.environ.get("REFRESH_INTERVAL_MINS"))

epd = epd2in7_V2.EPD()
current_dir = os.getcwd()
asset_dir = os.path.join(current_dir, 'assets')
font_path = os.path.join(asset_dir, 'Font.ttc')
font16 = ImageFont.truetype(font_path, 16)

def load_coins():
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}&vs_currency=usd&price_change_percentage=24h,7d,30d&ids={COINGECKO_CSV_IDS}"
        )
        return response.json()
    except Exception as e:
        logging.error(e.message)

def display_coins(coins):
    epd.init_Fast()
    image = Image.new("1", (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    current_y = PADDING
    for coin in coins:
        price = coin["current_price"]
        percent_change_24hr = round(coin["price_change_percentage_24h_in_currency"], PERCENT_DECIMALS)
        draw.text((PADDING, current_y), coin["name"], font=font16)
        draw.text((88 + PADDING, current_y), f"${price}", font=font16)
        draw.text((200 + PADDING, current_y), f"{percent_change_24hr}%", font=font16)
        current_y += 16 + PADDING * 3

    epd.display_Fast(epd.getbuffer(image))

def check_coins():
    while True:
        coins = load_coins()
        display_coins(coins)
        time.sleep(REFRESH_INTERVAL_MINS * 60)

def clear_screen():
    epd.init()
    epd.Clear()


def button_check():
    # pin numbers are interpreted as BCM pin numbers.
    GPIO.setmode(GPIO.BCM)
    # Sets the pin as input and sets Pull-up mode for the pin.
    GPIO.setup(KEY_1, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(KEY_2, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(KEY_3, GPIO.IN, GPIO.PUD_UP)
    GPIO.setup(KEY_4, GPIO.IN, GPIO.PUD_UP)

    while True:
        time.sleep(0.05)
        # Returns the value read at the given pin. It will be HIGH or LOW (0 or 1).

        if GPIO.input(KEY_1) == 0:
            logging.info("Key 1")
            while GPIO.input(KEY_1) == 0:
                time.sleep(0.01)

        elif GPIO.input(KEY_2) == 0:
            logging.info("Key 2")
            while GPIO.input(KEY_2) == 0:
                time.sleep(0.01)

        elif GPIO.input(KEY_3) == 0:
            logging.info("Key 3")
            while GPIO.input(KEY_3) == 0:
                time.sleep(0.01)

        elif GPIO.input(KEY_4) == 0:
            logging.info("Key 4")
            while GPIO.input(KEY_4) == 0:
                time.sleep(0.01)


def main():
    clear_screen()

    update_thread = threading.Thread(target=check_coins)
    update_thread.start()

    try:
        button_check()
    except KeyboardInterrupt:
        print("Program terminated. Cleaning up...")
        GPIO.cleanup()
        update_thread.join()


if __name__ == "__main__":
    main()
