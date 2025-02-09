# reference : https://bonory.tistory.com/80
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
    url='https://nid.naver.com/nidlogin.login'
    id='qhtlda2'
    pw='qhtld23'

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.add_argument("headless") # headless option
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)

    browser.implicitly_wait(2)

    browser.execute_script(f"document.getElementsByName('id')[0].value=\'{id}\'")
    browser.execute_script(f"document.getElementsByName('pw')[0].value=\'{pw}\'")

    browser.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()
    time.sleep(1)

    #browser.get(f'{cafemenuurl}&search.page={str(pageNum)}+ https://cafe.naver.com/gmsmgame?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D24065371%2526page%3D4%2526menuid%3D1%2526boardtype%3DL%2526articleid%3D158206%2526referrerAllArticles%3Dfalse')
    browser.get('https://cafe.naver.com/gmsmgame?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D24065371%2526page%3D4%2526menuid%3D1%2526boardtype%3DL%2526articleid%3D158206%2526referrerAllArticles%3Dfalse')

    
    print(browser.page_source)
    exit()
    soup = bs(browser.page_source, 'html.parser')
    soup = soup.find_all(class_ = '')[1]

    print(soup)
    exit()
    

    browser.close()
if __name__ == "__main__":
    main()