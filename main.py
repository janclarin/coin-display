import os
from xml.dom.minidom import NamedNodeMap
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
FONT_SIZE = 12
PADDING = 4
MAX_X = 260
PRICE_START_X = 60
PERCENT_1_START_X = 130
PERCENT_2_START_X = 174
PERCENT_3_START_X = 218

COINGECKO_CSV_IDS = os.environ.get("COINGECKO_CSV_IDS")
COINGECKO_DEMO_API_KEY = os.environ.get("COINGECKO_DEMO_API_KEY")
REFRESH_INTERVAL_MINS = int(os.environ.get("REFRESH_INTERVAL_MINS"))
PERCENT_TIME_COLUMN_1 = os.environ.get("PERCENT_TIME_COLUMN_1")
PERCENT_TIME_COLUMN_2 = os.environ.get("PERCENT_TIME_COLUMN_2")
PERCENT_TIME_COLUMN_3 = os.environ.get("PERCENT_TIME_COLUMN_3")

epd = epd2in7_V2.EPD()
current_dir = os.getcwd()
asset_dir = os.path.join(current_dir, "assets")
font_path = os.path.join(asset_dir, "Font.ttc")
font = ImageFont.truetype(font_path, FONT_SIZE)


def load_coins():
    try:
        percentages = ",".join([PERCENT_TIME_COLUMN_1, PERCENT_TIME_COLUMN_2, PERCENT_TIME_COLUMN_3])
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}&vs_currency=usd&price_change_percentage={percentages}&ids={COINGECKO_CSV_IDS}"
        )
        return response.json()
    except Exception as e:
        logging.error(e)


def round_sig_figures(num):
    if num > 1000:
        return f"{num}"
    elif num > 10:
        return f"{num:.2f}"

    price = float(f"{num:.3g}")
    return f"{price:g}"


def get_percent_change(coin, time_range):
    percent = coin[f"price_change_percentage_{time_range}_in_currency"]
    if percent is None:
        return "---"

    return f"{round(percent)}%"


def display_headers(draw):
    draw.text((PADDING, PADDING), "COIN", font=font)
    draw.text((PRICE_START_X + PADDING * 2, PADDING), "PRICE", font=font)
    draw.text(
        (PERCENT_1_START_X + PADDING * 2, PADDING),
        PERCENT_TIME_COLUMN_1.upper(),
        font=font,
    )
    draw.text(
        (PERCENT_2_START_X + PADDING * 2, PADDING),
        PERCENT_TIME_COLUMN_2.upper(),
        font=font,
    )
    draw.text(
        (PERCENT_3_START_X + PADDING * 2, PADDING),
        PERCENT_TIME_COLUMN_3.upper(),
        font=font,
    )

    header_line_y = FONT_SIZE + PADDING * 2
    draw.line((PADDING, header_line_y, MAX_X, header_line_y), fill=0)


def display_coin(coin, draw, y):
    logging.info(coin)
    ticker = str(coin["symbol"]).upper()
    price = round_sig_figures(coin["current_price"])
    percent_change_1 = get_percent_change(coin, PERCENT_TIME_COLUMN_1)
    percent_change_2 = get_percent_change(coin, PERCENT_TIME_COLUMN_2)
    percent_change_3 = get_percent_change(coin, PERCENT_TIME_COLUMN_3)
    draw.text((PADDING, y), ticker, font=font)
    draw.text((PRICE_START_X + PADDING * 2, y), f"${price}", font=font)
    draw.text((PERCENT_1_START_X + PADDING * 2, y), percent_change_1, font=font)
    draw.text((PERCENT_2_START_X + PADDING * 2, y), percent_change_2, font=font)
    draw.text((PERCENT_3_START_X + PADDING * 2, y), percent_change_3, font=font)


def display_coins(coins):
    epd.init_Fast()
    image = Image.new("1", (epd.height, epd.width), MAX_X)
    draw = ImageDraw.Draw(image)

    display_headers(draw)

    draw.line((PRICE_START_X, 0, PRICE_START_X, MAX_X), fill=0)
    draw.line((PERCENT_1_START_X, 0, PERCENT_1_START_X, MAX_X), fill=0)
    draw.line((PERCENT_2_START_X, 0, PERCENT_2_START_X, MAX_X), fill=0)
    draw.line((PERCENT_3_START_X, 0, PERCENT_3_START_X, MAX_X), fill=0)

    current_y = FONT_SIZE + PADDING * 4
    for coin in coins:
        display_coin(coin, draw, current_y)
        current_y += FONT_SIZE + PADDING * 2

    epd.display_Fast(epd.getbuffer(image))


def refresh_coins():
    coins = load_coins()
    display_coins(coins)


def check_coins():
    while True:
        refresh_coins()
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
            refresh_coins()
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
