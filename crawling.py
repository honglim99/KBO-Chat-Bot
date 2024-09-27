from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# Chrome 드라이버 실행 (경로가 설정되어 있지 않다면 경로를 명시적으로 설정해 주세요)
driver = webdriver.Chrome()

# 암묵적으로 웹 요소가 로드될 때까지 기다리는 시간 설정
driver.implicitly_wait(10)

# 타자 기록 페이지 URL
hitter_url = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"

# 페이지를 순차적으로 크롤링하는 함수
def crawl_table_data(base_url, csv_filename):
    driver.get(base_url)
    
    # 경기수(G) 기준으로 정렬하기 위해 클릭
    time.sleep(2)  # 페이지 로드 대기
    driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result > table > thead > tr > th:nth-child(5) > a').click()
    body1 = driver.find_element(By.CSS_SELECTOR, 'body')
    body1.click()
    time.sleep(2)  # 정렬이 완료될 때까지 잠시 대기

    all_data = []  # 모든 페이지의 데이터를 저장할 리스트

    # 페이지 순환을 위한 반복문 (최대 5페이지)
    for page_num in range(1, 6):  # 1페이지부터 5페이지까지
        print(f"{page_num} 페이지 크롤링 중...")

        # 테이블을 찾아서 크롤링
        table = driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result > table')
        table_df = pd.read_html(table.get_attribute('outerHTML'))[0]
        all_data.append(table_df)

        # 다음 페이지로 이동 (마지막 페이지는 버튼이 없으므로 종료)
        try:
            next_button = driver.find_element(By.ID, f"cphContents_cphContents_cphContents_ucPager_btnNo{page_num + 1}")
            next_button.click()
            time.sleep(3)  # 페이지 로드 대기
        except Exception as e:
            print(f"{page_num} 페이지까지 크롤링 완료.")
            break

    # 모든 페이지의 데이터를 합쳐서 DataFrame으로 변환
    final_df = pd.concat(all_data, ignore_index=True)

    # CSV 파일로 저장
    final_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"데이터가 {csv_filename}에 저장되었습니다.")

# 타자 기록 크롤링 함수
def crawl_hitter_data():
    crawl_table_data(hitter_url, 'hitter_data.csv')

# 투수 기록 크롤링 함수
def crawl_pitcher_data():
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.send_keys(Keys.PAGE_UP)
    time.sleep(1)
    # 투수 페이지로 이동
    pitcher_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="/Record/Player/PitcherBasic/Basic1.aspx"]'))
    )
    pitcher_button.click()
    
    # 투수 페이지 URL
    pitcher_url = driver.current_url
    
    # 투수 기록 크롤링
    crawl_table_data(pitcher_url, 'pitcher_data.csv')

# 타자 기록 크롤링 실행
crawl_hitter_data()

# 투수 기록 크롤링 실행
crawl_pitcher_data()

# 드라이버 종료
driver.quit()
