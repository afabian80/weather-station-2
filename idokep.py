#!/usr/bin/python3

import re
import requests
from datetime import timedelta
from timeloop import Timeloop


loop = Timeloop()
temp = "?"


@loop.job(interval=timedelta(seconds=10))
def update_screen():
    global temp
    print('Temperature: {} °C'.format(temp))


@loop.job(interval=timedelta(seconds=60))
def update_temperature():
    global temp
    try:
        page = requests.get('https://www.idokep.hu')
        p = re.compile('.*<div class="harminchat">.*<div class="homerseklet">(\d+)&deg;C</div>.*', re.DOTALL)
        m = p.match(page.text)
        temp = m.group(1)
        print('Updated temparature: {} °C'.format(temp))
    except AttributeError as e:
        print('Cannot parse time: {}'.format(e))
        raise


if __name__ == '__main__':
    update_temperature()
    loop.start(block=True)

