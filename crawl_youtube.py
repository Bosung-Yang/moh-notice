import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup as bs
import re
import pandas as pd

def crawl_youtube_community(channel_url, scroll_pause_time=2):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True) # 브라우저 종료 방지
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # chrome_options.add_argument("headless") # 필요하다면 headless 모드 사용

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(channel_url + "/community")  # 커뮤니티 탭으로 이동

    # 스크롤 다운을 통해 더 많은 게시글 로딩 (필요에 따라 횟수 조절)
    num_scrolls = 5  # 예시: 5번 스크롤
    for _ in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)

    # 로딩이 완료될 때까지 기다림 (명시적 대기)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-backstage-post-renderer")) # 게시글 요소가 나타날 때까지 대기
        )
    except:
        print("게시글 로딩 시간 초과")
        driver.quit()
        return []

    soup = bs(driver.page_source, 'html.parser')
    posts = soup.find_all("ytd-backstage-post-renderer")

    results = []
    for post in posts:
        try:
            # 게시글 내용 추출
            content = post.find("yt-formatted-string", {"id": "content-text"}).text.strip() if post.find("yt-formatted-string", {"id": "content-text"}) else ""

            # 댓글 수 추출 (댓글이 없는 경우 0으로 처리)
            comment_count_element = post.find("span", {"class": "style-scope ytd-comment-thread-renderer"})
            comment_count = int(re.sub(r"[^0-9]", "", comment_count_element.text)) if comment_count_element else 0

            # 게시 날짜 추출
            date_element = post.find("yt-formatted-string", {"class": "style-scope ytd-backstage-post-renderer"})
            date = date_element.text.strip() if date_element else ""

            results.append({"content": content, "comment_count": comment_count, "date": date})

        except AttributeError as e:
            print("Error parsing post:", e)
            continue # 오류가 발생한 게시글은 건너뜀

    driver.quit()
    return results

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ddinghoon/community"  # 크롤링하려는 유튜브 채널 URL
    data = crawl_youtube_community(channel_url)

    if data:
        df = pd.DataFrame(data)
        print(df)
        df.to_csv("youtube_community_data.csv", encoding="utf-8-sig", index=False) # csv 파일로 저장
