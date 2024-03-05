from django.test import TestCase

# Create your tests here.
from utils.broadcaster import Broadcaster

class TV_ProgramTestCase(TestCase):
    def setUp(self):

        pass
  
    def test_時間の24時間表記_1(self):
        data = [
            "08:00",
            "10:00",
            "11:30",
            "05:00",
            "09:00",
            "12:00"
        ]
        result = []
        pre_time = "00:00"
        broadcaster = Broadcaster()
        for value in data:  

            time = broadcaster.convert_time_to_24h_format(value,pre_time)
            print(time)
            pre_time = time
            result.append(time)

        answer = [
            "08:00",
            "10:00",
            "11:30",
            "17:00",
            "21:00",
            "00:00"
        ]
        
        self.assertAlmostEqual(answer,result)

    def test_時間の24時間表記_2(self):
        
        data = [
            "05:00",
            "03:00",
            "09:30",
            "12:00",
            "01:00"
        ]
        result = []
        pre_time = "00:00"
        broadcaster = Broadcaster()
        for value in data:  

            time = broadcaster.convert_time_to_24h_format(value,pre_time)
            print(time)
            pre_time = time
            result.append(time)

        answer = [
            "05:00",
            "15:00",
            "21:30",
            "00:00",
            "01:00"
            
        ]
        
        self.assertAlmostEqual(answer,result)
