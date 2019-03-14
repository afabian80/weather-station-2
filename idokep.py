#!/usr/bin/python2
import PIL
import re
import requests
import time
from PIL import Image, ImageFont, ImageDraw, ImageOps

from oled.device import ssd1306
from oled.serial import i2c

SCREEN_HOLD_SECONDS = 10

temp = "?"
serial = i2c(port=1, address=0x3c)
device = ssd1306(serial)
ttf = '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'
font60 = ImageFont.truetype(ttf, 60)


def update_screen():
    global temp
    print('Temperature: {} C'.format(temp))
    img = Image.new('L', (128, 64))
    draw = ImageDraw.Draw(img)
    draw.text((20, 0), temp + u"\u00B0", font=font60, fill=255)
    img_inv = PIL.ImageOps.invert(img)
    device.display(img.convert('1'))
    time.sleep(SCREEN_HOLD_SECONDS)
    device.display(img_inv.convert('1'))
    time.sleep(SCREEN_HOLD_SECONDS)


def update_temperature():
    global temp
    try:
        page = requests.get('https://www.idokep.hu')
        p = re.compile('.*<div class="harminchat">.*<div class="homerseklet">(\d+)&deg;C</div>.*', re.DOTALL)
        m = p.match(page.text)
        temp = m.group(1)
        print('Updated temperature: {} C'.format(temp))
    except AttributeError as e:
        print('Cannot parse time: {}'.format(e))
        raise


if __name__ == '__main__':
    t = 0
    while True:
        if t % 5 == 0:
            update_temperature()
        update_screen()
        t += 1

