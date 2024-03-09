
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from api.models import Program,Location,TVStation,Broadcast,Room
from datetime import datetime, timedelta,date

import unicodedata

import pytz
from django.utils import timezone
from datetime import timedelta


# 詳細は著作権違反になるかもしれないから取得しない
# https://bbs.bengo4.com/questions/291361/
# タイトルは問題なさそう

# とりあえず大阪と東京で使えるようにしたい

class Broadcaster():
    def __init__(self) -> None:
        self.options = Options()
        self.options.add_argument('--headless')
       
    def get_now_program(self,channel,location):
        # 現在放送中の番組を取得する
        location = Location.objects.get(name=location) 
        broadcast = Broadcast.objects.filter(channel=channel, location=location).first()
        print("broadcast",broadcast)
        if not broadcast  :
            return None
        
        now = timezone.now()
        
        current_program = Program.objects.filter(
            start_time__lte=now,
            end_time__gte=now,
            tv_station=broadcast.tv_station
        ).first()
        print("",current_program)
        return current_program
    
    def get_ABC_ASAHI(self):
        # schedule this_week
        # morning_tr    
        # cboxElement oa_time
        # program_overview title
        url = "https://www.asahi.co.jp/tvprogram/"
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        tv_station = TVStation.objects.get(name="ABC朝日放送")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(url)

        programs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".schedule .this_week"))
        )
        programs = self.driver.find_elements(By.CSS_SELECTOR, ".this_week tbody tr td:not(.time_cell)")
        today = timezone.now().date()
        # 前日に最後に保存したものを取得する
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
        is_next_day = False
        for row in programs:
            time_str = row.find_element(By.CSS_SELECTOR, "p.oa_time").text if row.find_elements(By.CSS_SELECTOR, 'p.oa_time') else None
            title = row.find_element(By.CSS_SELECTOR, "p.title").text  if row.find_elements(By.CSS_SELECTOR, 'p.title') else None
            if time_str and title:
                if time_str:
                    hour, minute = map(int, time_str.split(':'))
                    if hour == 0:
                        is_next_day = True
                    if hour >= 24:
                            is_next_day = True
                            hour -= 24

                    if is_next_day: 
                        program_date = datetime.today().date() + timedelta(days=1)
                    else:
                        program_date = datetime.today().date()
                    tz = pytz.timezone('Asia/Tokyo')
                    program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                    if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                    data = {
                        "title": title, 
                        "start_time":program_date,
                    }
                    title = self.zenkaku_to_hankaku(title)
                    room = self.create_room(title)
            

                    program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                    )

                    pre_program = program

                    print(title,program_time.time())



        self.driver.quit()

    def get_tvosaka(self):
        # timetables_weekly-timetable
        # program_desc
        url = "https://www.tv-osaka.co.jp/timetables/weekly/"
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        tv_station = TVStation.objects.get(name="テレビ大阪")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(url)
        
        programs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".timetables_weekly-timetable a"))
        )

        print(f"{len(programs)}番組を取得します")
        today = timezone.now().date()
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
        is_next_day = False
        for row in programs:
            time_str = row.find_element(By.CSS_SELECTOR, 'time').text if row.find_elements(By.CSS_SELECTOR, 'time') else None
            title = row.find_element(By.CSS_SELECTOR, 'cite').text if row.find_elements(By.CSS_SELECTOR, 'cite') else "タイトルなし"
            if not time_str and not title: 
                print("終了")
                return
            print(time_str)
            if time_str:
                hour, minute = map(int, time_str.split(':'))
                if hour == 0:
                    is_next_day = True
                if hour >= 24:
                        is_next_day = True
                        hour -= 24

                if is_next_day: 
                    program_date = datetime.today().date() + timedelta(days=1)
                else:
                    program_date = datetime.today().date()
                
                tz = pytz.timezone('Asia/Tokyo')
                program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                data = {
                        "title": title, 
                        "start_time":program_date,
                }
                title = self.zenkaku_to_hankaku(title)
                room = self.create_room(title)
            

                program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                )

                pre_program = program
                print(program_time.time(),title)
                
        self.driver.quit()

    
    def get_kansaiTV(self):
        url = "https://www.ktv.jp/timetable/"
        # timetable-content
        # program-airtime
        # program-summary_name
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        tv_station = TVStation.objects.get(name="関西テレビ")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(url)

        programs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".timetable-content .program"))
        )
        today = timezone.now().date()
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
        is_next_day = False
        print(len(programs),"番組を取得します")
        for row in programs:
            time_str = row.find_element(By.CSS_SELECTOR, '.program-airtime').text if row.find_elements(By.CSS_SELECTOR, '.program-airtime') else None
            title_elements = row.find_elements(By.CSS_SELECTOR, '.program-summary_name')
            title = title_elements[0].text if title_elements else "タイトルなし"

            if time_str:
                hour, minute = map(int, time_str.split(':'))
                if hour == 0:
                    is_next_day = True

                if is_next_day: 
                    program_date = datetime.today().date() + timedelta(days=1)
                else:
                    program_date = datetime.today().date()
                
                # program_time = datetime(program_date.year, program_date.month, program_date.day, hour, minute)

                tz = pytz.timezone('Asia/Tokyo')
                program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                title = self.zenkaku_to_hankaku(title)
                room = self.create_room(title)
            

                program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                )

                pre_program = program
                print(program_time.time(),title)
        self.driver.quit()





    def get_Asahi(self):
        tv_station = TVStation.objects.get(name="テレビ朝日")


        url = "https://www.tv-asahi.co.jp/bangumi/sphone/"
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(url)

        programs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".programList .item"))
        )
        today = timezone.now().date()
        # 前日に最後に保存したものを取得する
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
        print("---------------------------------------------")
        print("前日一番最後に放送されたもの",pre_program)
        print("---------------------------------------------")
        
        is_next_day = False
        for row in programs:
            time_str = row.find_element(By.CSS_SELECTOR, '.item__time').text if row.find_elements(By.CSS_SELECTOR, '.item__time') else None
            title_elements = row.find_elements(By.CSS_SELECTOR, '.item__title .item__anchor')
            title = title_elements[0].text if title_elements else "タイトルなし"
            # たまに 4:00 ~ 5:00のような形で表示されている場合がある
            # その場合はスキップする
            if "〜" in time_str:
                print("スキップ")
                continue
            # 0であれば日付が変わっている
            if time_str:
                hour, minute = map(int, time_str.split(':'))
                if hour == 0:
                    is_next_day = True

                if is_next_day: 
                    program_date = timezone.localdate() + timedelta(days=1)
                else:
                    program_date = timezone.localdate()
                
                # 番組の放送時刻
                
                tz = pytz.timezone('Asia/Tokyo')
                program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                title = self.zenkaku_to_hankaku(title)
                room = self.create_room(title)
            

                program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                )

                pre_program = program
                print(program_time.time(),title)
                

        

        self.driver.quit()




    def get_yomiuriTV_2(self):
        tv_station = TVStation.objects.get(name="読売テレビ")

        # スマホサイズに変更
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        }
        self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.driver = webdriver.Chrome(options=self.options)
        url = 'https://www.ytv.co.jp/program-weekly-smartphone/'
        self.driver.get(url)

        programs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".program_contents .program_table tbody tr td a "))
        )

        
        today = timezone.now().date()
        # 前日に最後に保存したものを取得する
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
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

                tz = pytz.timezone('Asia/Tokyo')
                program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                title = self.zenkaku_to_hankaku(title)
                room = self.create_room(title)
                print(title,program_time.time())

                program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                )

                pre_program = program
                print(program_time.time(),title)
            
                
        self.driver.quit()

    def get_all(self):
        print("-----------日本テレビ-----------")
        self.get_nihonTV_program()
        print("取得完了")
        print("-----------テレビ朝日放送-----------")
        self.get_ABC_ASAHI()
        print("取得完了")
        print("-----------朝日放送-----------")
        self.get_Asahi()
        print("取得完了")
        print("-----------関西てれび-----------")
        self.get_kansaiTV()
        print("取得完了")        
        print("-----------テレビ大阪-----------")
        self.get_tvosaka()
        print("取得完了")
        print("-----------読売テレビ-----------")
        self.get_yomiuriTV_2()
        print("取得完了")

    def get_nihonTV_program(self):
        print("日本テレビ")
        """ 今日一日の日本テレビの番組を取得する """

        self.driver = webdriver.Chrome(options=self.options)

        url = 'https://www.ntv.co.jp/program/'
        self.driver.get(url)

        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".program-common-display-title__day.program-common-display-title a"))
        )

        # 要素をクリック
        self.driver.execute_script("arguments[0].click();", element)



        programs = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".program-table__schedule__wrapper"))
        )

        tv_station = TVStation.objects.get(name="日本テレビ")

        is_next_day = False
        pre_time = "00:00"
        today = timezone.now().date()
        pre_program = Program.objects.filter(start_time=today,tv_station=tv_station)
        for program in programs:
            title = program.find_element(By.CSS_SELECTOR, '.program-table__schedule-description__title').text

            time_elements = program.find_elements(By.CSS_SELECTOR, '.program-table__schedule-time')
            time_str = time_elements[0].text if time_elements else "時間情報なし"
            if time_str:
                hour, minute = time_str.split(':')

                print("----------------------")
                # スタートが05なので次に00が来ればそれは日付を跨いだということ
                if hour == "00":
                    is_next_day = True
                
                if is_next_day:
                    print("日付が変わりました。")
                    program_date = datetime.today().date() + timedelta(days=1)
                else:
                    time = self.convert_time_to_24h_format(time_str,pre_time)
                    print("時間",time)
                    pre_time = time 
                    program_date = datetime.today().date()
                
                hour, minute = map(int, time.split(':'))

 
                tz = pytz.timezone('Asia/Tokyo')
                program_time = tz.localize(datetime(program_date.year, program_date.month, program_date.day, hour, minute))

                if pre_program:
                        pre_program.end_time = program_time + timedelta(minutes=-1)
                        pre_program.save()

                title = self.zenkaku_to_hankaku(title)
                room = self.create_room(title)
            

                program,created = Program.objects.get_or_create(
                        title=title,
                        tv_station=tv_station,
                        start_time=program_time,
                        room=room
                )

                pre_program = program
                print(program_time.time(),title)

        
            
        self.driver.quit()











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
            else:
                if prev_hours > current_hours :
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
    def create_room(self,title):
        room,created= Room.objects.get_or_create(name=title)
        return room
        

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
                        "station": "ABC朝日放送"
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
