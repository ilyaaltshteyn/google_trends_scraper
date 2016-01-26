# This script scrapes google trends data from a screenshot that it takes of a
# google trends chart for a given

from PIL import Image
import time
import numpy as np
import pandas as pd
import random
from selenium import webdriver

# Get list of proxy servers, pulled from http://www.google-proxy.net/
current_path = '/Users/ilya/Projects/stox/google_trends_scraper/'
proxies_list = pd.read_csv(current_path + 'google_proxies.csv')

def change_proxy(proxy_list):
    """ Creates and returns a webdriver instance with proxy settings adjusted. """

    address, port = np.array(proxies_list.ix[random.sample(proxies_list.index, 1)])[0]
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s:%s' % (str(address), str(port)))
    browser = webdriver.Chrome(executable_path = '/Users/ilya/Projects/WebDriver/chromedriver', 
                               chrome_options = options)
    return browser


def screen_cap(browser, path, keyword= 'aapl'):
    """ Takes a screenshot of the google trends chart for a given keyword. 
        Returns the location of the image. """

    url = 'http://www.google.com/trends/fetchComponent?hl=en-US&q= ' + \
        str(keyword) + '&cid=TIMESERIES_GRAPH_0&export=5&w=500&h=300'
    browser.get(url)
    time.sleep(3)
    browser.save_screenshot(path + keyword + '.png')
    browser.quit()

    return (path, keyword)

def read_image(path, name):
    """ Reads an image, spits out the data for the red line. """

    image = Image.open(path + name + '.png').convert('RGB')
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    reds = set(list(image.getdata()))
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
            if r < 90 and g > 100 and g < 160 and b > 210 and y > 370 and \
                y < 577 and x < 500:
                all_ys.append(y - 400)
        if len(all_ys) > 0:
            data['xs'].append(x)
            data['ys'].append(np.mean(all_ys))

    return (data, path, name)

def write_data(data, path, name):
    
    df = pd.DataFrame(data)
    df.to_csv(path + name + '.csv', index = False)

p, n = screen_cap(change_proxy(proxies_list), current_path)
d, p, n = read_image(p, n)
write_data(d, p, n)
