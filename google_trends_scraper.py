from PIL import Image
import requests

current_path = '/Users/ilya/Projects/stox/google_trends_scraper/'

import sys
import time
import numpy as np

from selenium import webdriver

def screen_cap(path, keyword= 'aapl'):
    """ Takes a screenshot of the google trends chart for a given keyword. 
        Returns the location of the image. """
    url = 'http://www.google.com/trends/fetchComponent?hl=en-US&q=aapl&cid=TIMESERIES_GRAPH_0&export=5&w=500&h=300'
    driver = webdriver.Chrome('/Users/ilya/Projects/WebDriver/chromedriver')
    driver.get(url)
    driver.save_screenshot(path + keyword + '.png')
    driver.quit()

    return (path, keyword)

def read_image(path, name):
    """ Reads an image, spits out the data for the red line. """
    image = Image.open(path + name + '.png').convert("RGB")
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    reds = set(list(image.getdata()))
    print reds
    x_size = image.size[0]
    y_size = image.size[1]
    data = {'xs': [], 'ys': [] }
    for x in range(0, x_size):
        all_ys = []
        for y in range (0, y_size):
            pixel = image.getpixel((x,y))
            r = pixel[0]
            g = pixel[1]
            b = pixel[2]
            if r < 90 and g > 100 and g < 160 and b > 210 and y > 370 and y < 577 and x < 500:
                all_ys.append(y - 400)
        if len(all_ys) > 0:
            data['xs'].append(x)
            data['ys'].append(np.mean(all_ys))

    return (data, path, name)

def write_data(data, path, name):
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(path + name + '.csv', index = False)

p, n = screen_cap(current_path)
d, p, n = read_image(p, n)
write_data(d, p, n)
