#!/usr/bin/python2
import PIL
import re
import requests
import time
from PIL import Image, ImageFont, ImageDraw, ImageOps
import logging
from requests import ConnectionError

from oled.device import ssd1306
from oled.serial import i2c

SCREEN_HOLD_SECONDS = 10
MAX_CONNECTION_ERRORS = 6

temp = "?"
connection_errors = 0
serial = i2c(port=1, address=0x3c)
device = ssd1306(serial)
ttf = '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'
font60 = ImageFont.truetype(ttf, 66)

logger = logging.getLogger('idokep')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('/var/log/idokep.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


def update_screen():
    global temp
    logger.debug('Temperature: %s C', temp)
    img = Image.new('L', (128, 64))
    draw = ImageDraw.Draw(img)
    temp_text = str(temp)
    text_size = draw.textsize(temp_text, font=font60)
    x_offset = (128 - text_size[0]) / 2
    draw.text((x_offset, 0), temp_text, font=font60, fill=255)
    img_inv = PIL.ImageOps.invert(img)
    device.display(img.convert('1'))
    time.sleep(SCREEN_HOLD_SECONDS)
    device.display(img_inv.convert('1'))
    time.sleep(SCREEN_HOLD_SECONDS)


def update_temperature():
    global temp
    global connection_errors
    try:
        page = requests.get('https://www.idokep.hu')
        connection_errors = 0
        p = re.compile('.*<div class="harminchat">.*<div class="homerseklet">(\d+)&deg;C</div>.*', re.DOTALL)
        m = p.match(page.text)
        temp = m.group(1)
        logger.info('Updated temperature: %s C', temp)
    except AttributeError as e:
        logger.error('Cannot parse temperature: %s', e)
        raise
    except ConnectionError as e:
        connection_errors += 1
        logger.error('Connection error: %s', e)
        logger.error('Remaining connection attempts: %d', MAX_CONNECTION_ERRORS - connection_errors)
        if connection_errors == MAX_CONNECTION_ERRORS:
            raise
    except Exception as e:
        logger.error('Unexpected error: %s', e)
        raise


if __name__ == '__main__':
    t = 0
    while True:
        if t % 30 == 0:
            update_temperature()
        update_screen()
        t += 1
