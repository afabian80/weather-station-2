#!/usr/bin/python2

import re
import requests
from datetime import timedelta
from timeloop import Timeloop
from oled.serial import i2c
from oled.device import ssd1306
from oled.render import canvas
from PIL import Image, ImageFont, ImageDraw, ImageOps
import time

loop = Timeloop()
temp = "?"
serial = i2c(port=1, address=0x3c)
device = ssd1306(serial)
ttf = '/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf'
font60 = ImageFont.truetype(ttf, 60)


@loop.job(interval=timedelta(seconds=2))
def update_screen():
    global temp
    print('Temperature: {} C'.format(temp))
    with canvas(device) as c:
        c.text((20,0), temp + u"\u00B0", font=font60, fill=255)
        time.sleep(1)


@loop.job(interval=timedelta(seconds=60))
def update_temperature():
    global temp
    try:
        page = requests.get('https://www.idokep.hu')
        p = re.compile('.*<div class="harminchat">.*<div class="homerseklet">(\d+)&deg;C</div>.*', re.DOTALL)
        m = p.match(page.text)
        temp = m.group(1)
        print('Updated temparature: {} C'.format(temp))
    except AttributeError as e:
        print('Cannot parse time: {}'.format(e))
        raise


if __name__ == '__main__':
    update_temperature()
    update_screen()
    loop.start(block=True)

