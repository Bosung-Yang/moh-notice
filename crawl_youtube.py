import selenium
from selenium import webdriver
import bs4 
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import csv
import pandas as pd
from bs4 import BeautifulSoup as bs
import re

def main():
    url = 'https://www.youtube.com/@ddinghoon/community'
    
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.add_argument("headless") # headless option
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)


    soup = bs(browser.page_source, 'html.parser')
    soup = soup.find_all(class_ = 'style-scope ytd-expander')

    print(soup)
if __name__ == "__main__":
    main()