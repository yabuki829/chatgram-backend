
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from api.models import Program,Location,TVStation,Broadcast
from datetime import datetime, timedelta,date

import unicodedata

class Broadcaster():
    def get_yomiuriTV_2(self):

        options = Options()
        # スマホサイズに変更
        mobile_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        options = Options()
        options.add_argument('--headless')
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        driver = webdriver.Chrome(options=options)

        url = 'https://www.ytv.co.jp/program-weekly-smartphone/'
        driver.get(url)

        programs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".program_contents .program_table tbody tr td a "))
        )
        tv_station = TVStation.objects.get(name="読売テレビ")
        is_next_day = False
        pre_time = "00:00"
        for row in programs:
            time_str = row.find_element(By.CSS_SELECTOR, '.time').text if row.find_elements(By.CSS_SELECTOR, '.time') else None
            title_element = row.find_elements(By.CSS_SELECTOR, '.ttl')
            if title_element:
                title = title_element[0].text
                title = title.replace("[二]", "").replace("[字]", "").replace("[デ]", "").replace("[解]", "").replace("[再]", "").replace("[解]", "")
            
            else:
                title = "No Title"

            
            if time_str:
                # 24時間制を考慮して時間を解析
                print("------------------------------------------------------------")
                hour, minute = map(int, time_str.split(':'))
                
                if hour >= 24:
                    print("24時間を超えています")
                    hour -= 24
                    program_date = datetime.today().date() + timedelta(days=1)
                else:
                    print("超えていません")
                    program_date = datetime.today().date()

                program_time = datetime(program_date.year, program_date.month, program_date.day, hour, minute)
                obj,created = Program.objects.get_or_create(
                    title=self.zenkaku_to_hankaku(title),
                    tv_station=tv_station,
                    date=program_date,
                    time=program_time.time() 
                )
                
            
                print(f"タイトル: {title}")
                print(program_date,program_time)

            

    def get_nihonTV_program(self):
        """ 今日一日の日本テレビの番組を取得する """

        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        url = 'https://www.ntv.co.jp/program/'
        driver.get(url)

        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".program-common-display-title__day.program-common-display-title a"))
        )

        # 要素をクリック
        driver.execute_script("arguments[0].click();", element)



        programs = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".program-table__schedule__wrapper"))
        )

        tv_station = TVStation.objects.get(name="日本テレビ")

        is_next_day = False
        pre_time = "00:00"
        for program in programs:
            title = program.find_element(By.CSS_SELECTOR, '.program-table__schedule-description__title').text
            detail_elements = program.find_elements(By.CSS_SELECTOR, '.program-table__schedule-description__text')
            detail = detail_elements[0].text if detail_elements else "詳細なし"

            time_elements = program.find_elements(By.CSS_SELECTOR, '.program-table__schedule-time')
            time = time_elements[0].text if time_elements else "時間情報なし"
            if time:
                hour, minute = time.split(":")

                print("----------------------")
                if hour == "00":
                    is_next_day = True
                
                if is_next_day:
                    program_date = datetime.today().date() + timedelta(days=1)
                   
                else:
                    time = self.convert_time_to_24h_format(time,pre_time)
                    pre_time = time 
                    program_date = datetime.today().date()

 
                program_time = self.convert_str_date(time,is_next_day)

                obj,created = Program.objects.get_or_create(
                    title=self.zenkaku_to_hankaku(title),
                    detail=detail,
                    tv_station=tv_station,
                    date=program_date,
                    time=program_time.time() 
                )
           
                print(f"タイトル: {title}")
                print(program_date,program_time)
            
        driver.quit()

    def convert_time_to_24h_format(self,current_time, prev_time=None):
        """
        時間文字列を24時間形式に変換する。前の時間も考慮して午後を判断する。
        :param current_time: 変換する時間文字列 ('HH:MM' 形式)
        :param prev_time: 前の時間文字列 ('HH:MM' 形式)、初めての時間の場合はNone
        :return: 24時間形式の時間文字列
        """
        current_hours, current_minutes = map(int, current_time.split(":"))
        
        if prev_time:
            prev_hours, _ = map(int, prev_time.split(":"))
            # 前の時間が12時以降（午後）で、現在の時間が0時から11時の場合、12時間加算
            if prev_hours >= 12 and current_hours < 12:
                current_hours += 12

        # 24時を超える時間の処理（例: 25時→1時）
        if current_hours >= 24:
            current_hours -= 24

        return f"{current_hours:02d}:{current_minutes:02d}"

    
    def convert_str_date(self,time_str,is_next_day):
        hour, minute = map(int, time_str.split(":"))
        if is_next_day:
            program_date = datetime.today().date() + timedelta(days=1)
        else:
            program_date = datetime.today().date()


        # datetimeオブジェクトを構築
        program_time = datetime(program_date.year, program_date.month, program_date.day, hour, minute)
        return  program_time
    
    def zenkaku_to_hankaku(self,text):
        """
        全角文字を半角文字に変換する。
        :param text: 変換する文字列
        :return: 半角文字に変換された文字列
        """
        return unicodedata.normalize("NFKC", text)

    def add_broadcast(self):
        broads = [
            {"location": "北海道(札幌)", "broadcast": [
                {
                    "channel":1,
                    "station":"HBC北海道放送"
                    
                },
                {
                    "channel":2,
                    "station":"NHKEテレ"
                    
                },
                {
                    "channel":3,
                    "station":"NHK総合"
                    
                },
                {
                    "channel":5,
                    "station":"札幌テレビ"
                    
                },
                {
                    "channel":6,
                    "station":"北海道テレビ"
                    
                },
                {
                    "channel":7,
                    "station":"テレビ北海道"
                    
                },
                {
                    "channel":8,
                    "station":"北海道文化放送"
                    
                },
            ]},
            {"location": "青森", "broadcast": []},
            {"location": "秋田", "broadcast": []},
            {"location": "岩手", "broadcast": []},
            {"location": "宮城", "broadcast": []},
            {"location": "山形", "broadcast": []},
            {"location": "福島", "broadcast": []},
            {"location": "茨城", "broadcast": []},
            {"location": "栃木", "broadcast": []},
            {"location": "群馬", "broadcast": []},
            {"location": "埼玉", "broadcast": []},
            {"location": "千葉", "broadcast": []},
            {"location": "東京", "broadcast": [
                {
                        "channel": 1,
                        "station": "NHK総合"
                    },
                    {
                        "channel": 2,
                        "station": "NHK Eテレ"
                    },
                    {
                        "channel": 4,
                        "station": "日本テレビ"
                    },
                    {
                        "channel": 5,
                        "station": "テレビ朝日"
                    },
                    {
                        "channel": 6,
                        "station": "TBSテレビ"
                    },
                    {
                        "channel": 7,
                        "station": "テレビ東京"
                    },
                    {
                        "channel": 8,
                        "station": "フジテレビ"
                    }
            ]},
            {"location": "神奈川", "broadcast": []},
            {"location": "新潟", "broadcast": []},
            {"location": "富山", "broadcast": []},
            {"location": "石川", "broadcast": []},
            {"location": "福井", "broadcast": []},
            {"location": "山梨", "broadcast": []},
            {"location": "長野", "broadcast": []},
            {"location": "岐阜", "broadcast": []},
            {"location": "静岡", "broadcast": []},
            {"location": "愛知", "broadcast": []},
            {"location": "三重", "broadcast": []},
            {"location": "滋賀", "broadcast": []},
            {"location": "京都", "broadcast": []},
            {"location": "大阪", "broadcast": [
                 {
                        "channel": 10,
                        "station": "読売テレビ"
                    },
                    {
                        "channel": 8,
                        "station": "関西テレビ"
                    },
                    {
                        "channel": 4,
                        "station": "毎日放送"
                    },
                    {
                        "channel": 6,
                        "station": "朝日放送テレビ"
                    },
                    {
                        "channel": 7,
                        "station": "テレビ大阪"
                    },
                    {
                        "channel": 1,
                        "station": "NHK総合"
                    },
                    {
                        "channel": 3,
                        "station": "NHK教育"
                    }
            ]},
            {"location": "兵庫", "broadcast": []},
            {"location": "奈良", "broadcast": []},
            {"location": "和歌山", "broadcast": []},
            {"location": "鳥取", "broadcast": []},
            {"location": "島根", "broadcast": []},
            {"location": "岡山", "broadcast": []},
            {"location": "広島", "broadcast": []},
            {"location": "山口", "broadcast": []},
            {"location": "徳島", "broadcast": []},
            {"location": "香川", "broadcast": []},
            {"location": "愛媛", "broadcast": []},
            {"location": "高知", "broadcast": []},
            {"location": "福岡", "broadcast": []},
            {"location": "佐賀", "broadcast": []},
            {"location": "長崎", "broadcast": []},
            {"location": "熊本", "broadcast": []},
            {"location": "大分", "broadcast": []},
            {"location": "宮崎", "broadcast": []},
            {"location": "鹿児島", "broadcast": []},
            {"location": "沖縄", "broadcast": []}
        ]
        
        for borad in broads:
            print("------------------------")
            print(borad["location"],"の放送番組")
            location ,created=  Location.objects.get_or_create(name=borad["location"])
        
            for data in borad["broadcast"]:
                tv_station ,created = TVStation.objects.get_or_create(name=data["station"])
                print(location)
                print(tv_station)
                obj, created = Broadcast.objects.get_or_create(tv_station=tv_station,location=location,channel=data["channel"])
                
                if created:
                    print(obj)
                else:
                    print("既に作成済みです:",obj)
        

    
# 04:30
# 05:50
# 09:00
# 11:10
# 11:20
# 11:30
# 11:45
# 11:55
# 01:55
# 03:50
# 07:00
# 09:00
# 09:54
# 10:00
# 11:00
# 11:59
# 00:54
# 00:59
# 01:29
# 01:59
# 02:29
# 03:29
# 03:59
       