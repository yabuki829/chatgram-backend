from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Program,Location,TVStation,Broadcast
from .serializers import ProgramSerializer
from django.utils import timezone

from django.utils import timezone
from datetime import time,datetime,timedelta

from utils.broadcaster import Broadcaster




class ProgramList(APIView):
    def get(self, request):
        # 都道府県とchannelで分ける
        # 取得例) 大阪の10channelを取得する
        # データの中を確認して location, channel を取得する
        print(self.request.GET["channel"])
        print(self.request.GET["location"])
        channel = self.request.GET["channel"]
        
        broadcaster = Broadcaster()
        program = broadcaster.get_now_program(channel,self.request.GET["location"])
        if program:
            serializer = ProgramSerializer(program)
        else:
            return Response({"message": "現在非対応です。"})
            
        return Response(serializer.data)
    




 

from rest_framework.decorators import api_view
@api_view(['GET'])
def test(request):
    
    broadcaster = Broadcaster()
    broadcaster.get_all()
 

    channel = 4
    location = "東京"
    broadcaster = Broadcaster()
    program = broadcaster.get_now_program(channel,location)
    if program:
        serializer = ProgramSerializer(program)
    else:
        return Response({"message": "現在非対応です。"})
            
    return Response(serializer.data)


def get_tv():
        print("番組を取得します")
        location = Location.objects.get(name="大阪")
        today = timezone.localdate() + timedelta(days=1)
        start_of_today = timezone.make_aware(datetime.combine(today, time.min))
        end_of_today = timezone.make_aware(datetime.combine(today, time.max))
        channel = 6
        broadcast = Broadcast.objects.filter(channel=channel, location=location).first()

        if broadcast:
            programs_today = Program.objects.filter(
                start_time__gte=start_of_today,
                start_time__lte=end_of_today
            ).order_by('start_time')
            print(programs_today.last())
            # serializer = ProgramSerializer(programs_today, many=True)
        else:
            print("指定された条件に一致するBroadcastが見つかりません。")
            Response({"message": "現在非対応です。"})

        
