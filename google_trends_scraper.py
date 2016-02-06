# This script scrapes google trends data from a screenshot that it takes of a
# google trends chart for a given keyword.

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
    """ proxy_list should be a pandas dataframe with proxy address and port.
        Creates and returns a webdriver instance with proxy settings adjusted. """

    address, port = np.array(proxy_list.ix[random.sample(proxy_list.index, 
                                                                1)])[0]
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s:%s' % (str(address), str(port)))
    browser = webdriver.Chrome(executable_path = 
                               '/Users/ilya/Projects/WebDriver/chromedriver', 
                               chrome_options = options)
    return browser

def screen_cap(proxy_list, path, keyword= 'aapl'):
    """ Takes a screenshot of the google trends chart for a given keyword. 
        Returns the location of the image. """

    browser = change_proxy(proxy_list)

    for attempt in range(5):
        try:
            url = 'http://www.google.com/trends/fetchComponent?hl=en-US&q= ' + \
                str(keyword) + '&cid=TIMESERIES_GRAPH_0&export=5&w=500&h=300'
            browser.get(url)
            time.sleep(3) # Update to use selenium's explicit wait
            browser.save_screenshot(path + keyword + '.png')
            browser.quit()

            return (path, keyword)

        except Exception as e:
            print e
            browser = change_proxy(proxy_list)
            continue

def read_image(path, name):
    """ Reads an image, spits out the data for the blue line. """

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
    """ Writes scraped data to path + name + .csv"""
    
    df = pd.DataFrame(data)
    df.to_csv(path + name + '.csv', index = False)

if __name__ == "__main__":
    p, n = screen_cap(proxies_list, current_path)
    d, p, n = read_image(p, n)
    write_data(d, p, n)