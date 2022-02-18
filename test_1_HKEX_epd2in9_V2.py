#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Test HKEX epd2in9_V2
# Version : 0.1

import time, datetime
import os, sys, requests, re, json
from PIL import Image, ImageFont, ImageDraw
from data_folder import epd2in9_V2

stock_no = '0388'

delay = 30  #60 = 1 min

refresh = 20

test_icon = 'RPi.bmp'
icon_size = 96, 96

# Folder directory
basedir = os.path.dirname(os.path.realpath(__file__))
icondir = os.path.join(basedir, 'icons')
fontdir = os.path.join(basedir, 'fonts')
tempdir = os.path.join(basedir, 'temp')

# Font setting
font15 = ImageFont.truetype(os.path.join(fontdir, 'FreeSans.ttf'), 15)
font18 = ImageFont.truetype(os.path.join(fontdir, 'FreeSans.ttf'), 18)
font24 = ImageFont.truetype(os.path.join(fontdir, 'FreeSans.ttf'), 24)
font36 = ImageFont.truetype(os.path.join(fontdir, 'FreeSans.ttf'), 36)
font48 = ImageFont.truetype(os.path.join(fontdir, 'FreeSans.ttf'), 48)

def get_stock():

    res = requests.get(f'https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities/Equities-Quote?sym={stock_no}&sc_lang=zh-HK')
    m = re.search('LabCI.getToken = function \(\) { (.+?); };', ' '.join(res.text.split()) )
    token = m.group(1).split('return')[-1].replace('"','').strip()
    dt = int(time.mktime(datetime.datetime.now().timetuple()))
    res = requests.get(f'https://www1.hkex.com.hk/hkexwidget/data/getchartdata2?hchart=1&span=0&int=0&ric={stock_no}.HK&token={token}&qid={dt}&callback=jQuery_{dt}')
    m2 = re.match('jQuery_\d+\((.+)\)',res.text)
    jd = json.loads(m2.group(1))

    print ('Stock no. : ', stock_no)
    i = len(jd['data']['datalist'])-2

    n = int(str(jd['data']['datalist'][i][0])[0:10])
    strDate = time.strftime("%Y-%m-%d", time.localtime(n))
    strTime = time.strftime("%H : %M", time.localtime(n))

    price = '$'+str(jd['data']['datalist'][i][4])
    vol = str(jd['data']['datalist'][i][5])

    print (strDate, strTime)
    print('Price  :', price)
    print('Volume :', vol, '\n')

    draw.rectangle((5, 0, 200, 40), fill = 1, outline=1)
    draw.text((5,0), strTime, font = font36, fill = 0)

    draw.rectangle((5, 40, 200, 80), fill = 1, outline=1)
    draw.text((5,40), 'Vol. '+ vol, font = font36, fill = 0)

    draw.rectangle((5, 80 ,200, 127), fill = 1, outline=1)
    draw.text((5, 80), price, font=font48, fill=0)

    # newimage = Himage.crop([5, 0, 200, 127])
    # Himage.paste(newimage, (5,0))

    epd.display_Partial(epd.getbuffer(Himage))
    Himage.save(os.path.join(tempdir, 'Temp_test_HKEX.bmp'))

    time.sleep(delay)

def draw_stock_no():
    current_W = 96
    text_W, text_H = draw.textsize(stock_no, font=font24)
    draw.text((int((current_W-text_W)/2+200), 10), stock_no, font=font24, fill=0)

def draw_Icon():
    test_logo = Image.open(os.path.join(icondir, test_icon))         
    test_logo = test_logo.resize(icon_size)
    Himage.paste(test_logo, (201, 32))

def epaper_Clear():
    epd.init()
    epd.Clear(0xFF)

def epaper_Exit():
    epd = epd2in9_V2.EPD()
    epd.init()
    epd.Clear(0xFF)
    epd2in9_V2.epdconfig.module_exit()

try:
    epd = epd2in9_V2.EPD()
    epaper_Clear()

    Himage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Himage)

    draw_stock_no()
    draw_Icon()

    epd.display_Base(epd.getbuffer(Himage))
    
    counter = 0
    while True:
        get_stock()
        # print(counter)
        counter += 1
        if counter > refresh :
            print('Refresh...')
            epaper_Clear()
            epd.display_Base(epd.getbuffer(Himage))
            counter = 0
            
except KeyboardInterrupt:
    print('leaning...')
    epaper_Exit()
    print("Exit!")
    exit()